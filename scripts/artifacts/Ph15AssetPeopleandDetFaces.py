# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses basic asset record data from Photos.sqlite to include people and detected face data supports iOS 14-17.
#   The results could produce multiple records for a single asset.
#   This parser is based on research and SQLite queries written by Scott Koenig
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
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph15assetpeopledetfacephdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite basic asset people and face data from iOS " + iosversion)
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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',        
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zAsset.ZFACEAREAPOINTS > 0      
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[60] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[60])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[10])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[78] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_FaceCropFor_' + row[74] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[78])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59],
                                personcontactmatchingdictionary,
                                row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77],
                                facecropresourcedata_blob,
                                row[79], row[80], row[81],
                                row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                                row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                row[132], row[133], row[134]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 14.'
            report = ArtifactHtmlReport('Photos.sqlite-People_Faces_Data')
            report.start_artifact_report(report_folder, 'Ph15.1-People & Faces Asset Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAsset-Trashed Date-13',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                            'zAsset-Saved Asset Type-15',
                            'zAddAssetAttr-Creator Bundle ID-16',
                            'zAddAssetAttr-Imported By Display Name-17',
                            'zAddAssetAttr-Imported by-18',
                            'zCldMast-Imported by Bundle ID-19',
                            'zCldMast-Imported by Display Name-20',
                            'zCldMast-Imported By-21',
                            'zAsset-Visibility State-22',
                            'zExtAttr-Camera Make-23',
                            'zExtAttr-Camera Model-24',
                            'zExtAttr-Lens Model-25',
                            'zAsset-Derived Camera Capture Device-26',
                            'zAddAssetAttr-Camera Captured Device-27',
                            'zAddAssetAttr-Share Type-28',
                            'zCldMast-Cloud Local State-29',
                            'zCldMast-Import Date-30',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-31',
                            'zAddAssetAttr-Import Session ID-32',
                            'zAddAssetAttr-Alt Import Image Date-33',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-34',
                            'zAsset-Cloud Batch Publish Date-35',
                            'zAsset-Cloud Server Publish Date-36',
                            'zAsset-Cloud Download Requests-37',
                            'zAsset-Cloud Batch ID-38',
                            'zAsset-Latitude-39',
                            'zExtAttr-Latitude-40',
                            'zAsset-Longitude-41',
                            'zExtAttr-Longitude-42',
                            'zAddAssetAttr-GPS Horizontal Accuracy-43',
                            'zAddAssetAttr-Location Hash-44',
                            'zAddAssetAttr-Shifted Location Valid-45',
                            'zAddAssetAttr-Shifted Location Data-46',
                            'zAddAssetAttr-Reverse Location Is Valid-47',
                            'zAddAssetAttr-Reverse Location Data-48',
                            'AAAzCldMastMedData-zOPT-49',
                            'zAddAssetAttr-Media Metadata Type-50',
                            'AAAzCldMastMedData-Data-51',
                            'CldMasterzCldMastMedData-zOPT-52',
                            'zCldMast-Media Metadata Type-53',
                            'CMzCldMastMedData-Data-54',
                            'zFaceCrop-Face Area Points-55',
                            'zAsset-Face Adjustment Version-56',
                            'zAddAssetAttr-Face Regions-57',
                            'zDetFace-Asset Visible-58',
                            'zDetFacePrint-Data-59',
                            'zPerson-Contact Matching Dictionary-60',
                            'zPerson-Face Count-61',
                            'zDetFace-Face Crop-62',
                            'zDetFace-Face Algorithm Version-63',
                            'zDetFace-Adjustment Version-64',
                            'zDetFace-UUID-65',
                            'zPerson-Person UUID-66',
                            'zDetFace-Confirmed Face Crop Generation State-67',
                            'zDetFace-Manual-68',
                            'zDetFace-VIP Model Type-69',
                            'zDetFace-Name Source-70',
                            'zDetFace-Cloud Name Source-71',
                            'zPerson-Person URI-72',
                            'zPerson-Display Name-73',
                            'zPerson-Full Name-74',
                            'zPerson-Cloud Verified Type-75',
                            'zFaceCrop-State-76',
                            'zFaceCrop-Type-77',
                            'zFaceCrop-Resource Data-78',
                            'zFaceCrop-UUID-79',
                            'zPerson-Type-80',
                            'zPerson-Verified Type-81',
                            'zPerson-Gender Type-82',
                            'zDetFace-Gender Type-83',
                            'zDetFace-Center X-84',
                            'zDetFace-Center Y-85',
                            'zPerson-Age Type Estimate-86',
                            'zDetFace-Age Type Estimate-87',
                            'zDetFace-Hair Color Type-88',
                            'zDetFace-Facial Hair Type-89',
                            'zDetFace-Has Smile-90',
                            'zDetFace-Smile Type-91',
                            'zDetFace-Lip Makeup Type-92',
                            'zDetFace-Eyes State-93',
                            'zDetFace-Is Left Eye Closed-94',
                            'zDetFace-Is Right Eye Closed-95',
                            'zDetFace-Eye Glasses Type-96',
                            'zDetFace-Eye Makeup Type-97',
                            'zDetFace-Cluster Squence Number Key-98',
                            'zDetFace-Grouping ID-99',
                            'zDetFace-Master ID-100',
                            'zDetFace-Quality-101',
                            'zDetFace-Quality Measure-102',
                            'zDetFace-Source Height-103',
                            'zDetFace-Source Width-104',
                            'zDetFace-Hidden/Asset Hidden-105',
                            'zDetFace-In Trash/Recently Deleted-106',
                            'zDetFace-Cloud Local State-107',
                            'zDetFace-Training Type-108',
                            'zDetFace.Pose Yaw-109',
                            'zDetFace-Roll-110',
                            'zDetFace-Size-111',
                            'zDetFace-Cluster Squence Number-112',
                            'zDetFace-Blur Score-113',
                            'zDetFacePrint-Face Print Version-114',
                            'zMedAnlyAstAttr-Face Count-115',
                            'zDetFaceGroup-UUID-116',
                            'zDetFaceGroup-Person Builder State-117',
                            'zDetFaceGroup-UnNamed Face Count-118',
                            'zPerson-In Person Naming Model-119',
                            'zPerson-Key Face Pick Source Key-120',
                            'zPerson-Manual Order Key-121',
                            'zPerson-Question Type-122',
                            'zPerson-Suggested For Client Type-123',
                            'zPerson-Merge Target Person-124',
                            'zPerson-Cloud Local State-125',
                            'zFaceCrop-Cloud Local State-126',
                            'zFaceCrop-Cloud Type-127',
                            'zPerson-Cloud Delete State-128',
                            'zFaceCrop-Cloud Delete State-129',
                            'zFaceCrop-Invalid Merge Candidate Person UUID-130',
                            'zAsset-zPK-131',
                            'zAddAssetAttr-zPK-132',
                            'zAsset-UUID = store.cloudphotodb-133',
                            'zAddAssetAttr-Master Fingerprint-134')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite people faces and basic asset data data')

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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP       
        WHERE zAsset.ZFACEAREAPOINTS > 0  
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[65] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[65])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[10])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[85] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_FaceCropFor_' + row[81] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[85])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64],
                                personcontactmatchingdictionary,
                                row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                row[82], row[83], row[84],
                                facecropresourcedata_blob,
                                row[86], row[87], row[88], row[89], row[90],
                                row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                                row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
                                row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 15.'
            report = ArtifactHtmlReport('Photos.sqlite-People_Faces_Data')
            report.start_artifact_report(report_folder, 'Ph15.1-People & Faces Asset Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                            'zAsset- Conversation= zGenAlbum_zPK -14',
                            'zAsset-Syndication State-15',
                            'zAsset-Trashed Date-16',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-17',
                            'zAsset-Saved Asset Type-18',
                            'zAddAssetAttr-Imported by Bundle ID-19',
                            'zAddAssetAttr-Imported By Display Name-20',
                            'zAddAssetAttr-Imported by-21',
                            'zCldMast-Imported by Bundle ID-22',
                            'zCldMast-Imported by Display Name-23',
                            'zCldMast-Imported By-24',
                            'zAsset-Visibility State-25',
                            'zExtAttr-Camera Make-26',
                            'zExtAttr-Camera Model-27',
                            'zExtAttr-Lens Model-28',
                            'zAsset-Derived Camera Capture Device-29',
                            'zAddAssetAttr-Camera Captured Device-30',
                            'zAddAssetAttr-Share Type-31',
                            'zCldMast-Cloud Local State-32',
                            'zCldMast-Import Date-33',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-34',
                            'zAddAssetAttr-Import Session ID-35',
                            'zAddAssetAttr-Alt Import Image Date-36',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-37',
                            'zAsset-Cloud Batch Publish Date-38',
                            'zAsset-Cloud Server Publish Date-39',
                            'zAsset-Cloud Download Requests-40',
                            'zAsset-Cloud Batch ID-41',
                            'zAsset-Latitude-42',
                            'zExtAttr-Latitude-43',
                            'zAsset-Longitude-44',
                            'zExtAttr-Longitude-45',
                            'zAddAssetAttr-GPS Horizontal Accuracy-46',
                            'zAddAssetAttr-Location Hash-47',
                            'zAddAssetAttr-Shifted Location Valid-48',
                            'zAddAssetAttr-Shifted Location Data-49',
                            'zAddAssetAttr-Reverse Location Is Valid-50',
                            'zAddAssetAttr-Reverse Location Data-51',
                            'AAAzCldMastMedData-zOPT-52',
                            'zAddAssetAttr-Media Metadata Type-53',
                            'AAAzCldMastMedData-Data-54',
                            'CldMasterzCldMastMedData-zOPT-55',
                            'zCldMast-Media Metadata Type-56',
                            'CMzCldMastMedData-Data-57',
                            'zAsset-Bundle Scope-58',
                            'zFaceCrop-Face Area Points-59',
                            'zAsset-Face Adjustment Version-60',
                            'zAddAssetAttr-Face Regions-61',
                            'zAddAssetAttr-Face Analysis Version-62',
                            'zDetFace-Asset Visible-63',
                            'zDetFacePrint-Data-64',
                            'zPerson-Contact Matching Dictionary-65',
                            'zPerson-Face Count-66',
                            'zDetFace-Face Crop-67',
                            'zDetFace-Face Algorithm Version-68',
                            'zDetFace-Adjustment Version-69',
                            'zDetFace-UUID-70',
                            'zPerson-Person UUID-71',
                            'zDetFace-Confirmed Face Crop Generation State-72',
                            'zDetFace-Manual-73',
                            'zDetFace-Detection Type-74',
                            'zPerson-Detection Type-75',
                            'zDetFace-VIP Model Type-76',
                            'zDetFace-Name Source-77',
                            'zDetFace-Cloud Name Source-78',
                            'zPerson-Person URI-79',
                            'zPerson-Display Name-80',
                            'zPerson-Full Name-81',
                            'zPerson-Cloud Verified Type-82',
                            'zFaceCrop-State-83',
                            'zFaceCrop-Type-84',
                            'zFaceCrop-Resource Data-85',
                            'zFaceCrop-UUID-86',
                            'zPerson-Type-87',
                            'zPerson-Verified Type-88',
                            'zPerson-Gender Type-89',
                            'zDetFace-Gender Type-90',
                            'zDetFace-Center X-91',
                            'zDetFace-Center Y-92',
                            'zPerson-Age Type Estimate-93',
                            'zDetFace-Age Type Estimate-94',
                            'zDetFace-Ethnicity Type-95',
                            'zDetFace-Skin Tone Type-96',
                            'zDetFace-Hair Type-97',
                            'zDetFace-Hair Color Type-98',
                            'zDetFace-Head Gear Type-99',
                            'zDetFace-Facial Hair Type-100',
                            'zDetFace-Has Face Mask-101',
                            'zDetFace-Pose Type-102',
                            'zDetFace-Face Expression Type-103',
                            'zDetFace-Has Smile-104',
                            'zDetFace-Smile Type-105',
                            'zDetFace-Lip Makeup Type-106',
                            'zDetFace-Eyes State-107',
                            'zDetFace-Is Left Eye Closed-108',
                            'zDetFace-Is Right Eye Closed-109',
                            'zDetFace-Gaze Center X-110',
                            'zDetFace-Gaze Center Y-111',
                            'zDetFace-Face Gaze Type-112',
                            'zDetFace-Eye Glasses Type-113',
                            'zDetFace-Eye Makeup Type-114',
                            'zDetFace-Cluster Squence Number Key-115',
                            'zDetFace-Grouping ID-116',
                            'zDetFace-Master ID-117',
                            'zDetFace-Quality-118',
                            'zDetFace-Quality Measure-119',
                            'zDetFace-Source Height-120',
                            'zDetFace-Source Width-121',
                            'zDetFace-Hidden/Asset Hidden-122',
                            'zDetFace-In Trash/Recently Deleted-123',
                            'zDetFace-Cloud Local State-124',
                            'zDetFace-Training Type-125',
                            'zDetFace.Pose Yaw-126',
                            'zDetFace-Body Center X-127',
                            'zDetFace-Body Center Y-128',
                            'zDetFace-Body Height-129',
                            'zDetFace-Body Width-130',
                            'zDetFace-Roll-131',
                            'zDetFace-Size-132',
                            'zDetFace-Cluster Squence Number-133',
                            'zDetFace-Blur Score-134',
                            'zDetFacePrint-Face Print Version-135',
                            'zMedAnlyAstAttr-Face Count-136',
                            'zDetFaceGroup-UUID-137',
                            'zDetFaceGroup-Person Builder State-138',
                            'zDetFaceGroup-UnNamed Face Count-139',
                            'zPerson-In Person Naming Model-140',
                            'zPerson-Key Face Pick Source Key-141',
                            'zPerson-Manual Order Key-142',
                            'zPerson-Question Type-143',
                            'zPerson-Suggested For Client Type-144',
                            'zPerson-Merge Target Person-145',
                            'zPerson-Cloud Local State-146',
                            'zFaceCrop-Cloud Local State-147',
                            'zFaceCrop-Cloud Type-148',
                            'zPerson-Cloud Delete State-149',
                            'zFaceCrop-Cloud Delete State-150',
                            'zFaceCrop-Invalid Merge Canidate Person UUID-151',
                            'zAsset-zPK-152',
                            'zAddAssetAttr-zPK-153',
                            'zAsset-UUID = store.cloudphotodb-154',
                            'zAddAssetAttr-Master Fingerprint-155')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite people faces and basic asset data data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',       
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zAsset.ZFACEAREAPOINTS > 0  
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[66] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[66])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[10])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[87] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_FaceCropFor_' + row[83] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[87])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65],
                                personcontactmatchingdictionary,
                                row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                row[82], row[83], row[84], row[85], row[86],
                                facecropresourcedata_blob,
                                row[88], row[89], row[90],
                                row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                                row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
                                row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
                                row[156], row[157], row[158]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 16.'
            report = ArtifactHtmlReport('Photos.sqlite-People_Faces_Data')
            report.start_artifact_report(report_folder, 'Ph15.1-People & Faces Asset Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                            'zAsset- Conversation= zGenAlbum_zPK-14',
                            'zAsset-Syndication State-15',
                            'zAsset-Trashed Date-16',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-17',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-18',
                            'zAsset-Saved Asset Type-19',
                            'zAddAssetAttr-Imported by Bundle ID-20',
                            'zAddAssetAttr-Imported By Display Name-21',
                            'zAddAssetAttr-Imported by-22',
                            'zCldMast-Imported by Bundle ID-23',
                            'zCldMast-Imported by Display Name-24',
                            'zCldMast-Imported By-25',
                            'zAsset-Visibility State-26',
                            'zExtAttr-Camera Make-27',
                            'zExtAttr-Camera Model-28',
                            'zExtAttr-Lens Model-29',
                            'zAsset-Derived Camera Capture Device-30',
                            'zAddAssetAttr-Camera Captured Device-31',
                            'zAddAssetAttr-Share Type-32',
                            'zCldMast-Cloud Local State-33',
                            'zCldMast-Import Date-34',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-35',
                            'zAddAssetAttr-Import Session ID-36',
                            'zAddAssetAttr-Alt Import Image Date-37',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-38',
                            'zAsset-Cloud Batch Publish Date-39',
                            'zAsset-Cloud Server Publish Date-40',
                            'zAsset-Cloud Download Requests-41',
                            'zAsset-Cloud Batch ID-42',
                            'zAsset-Latitude-43',
                            'zExtAttr-Latitude-44',
                            'zAsset-Longitude-45',
                            'zExtAttr-Longitude-46',
                            'zAddAssetAttr-GPS Horizontal Accuracy-47',
                            'zAddAssetAttr-Location Hash-48',
                            'zAddAssetAttr-Shifted Location Valid-49',
                            'zAddAssetAttr-Shifted Location Data-50',
                            'zAddAssetAttr-Reverse Location Is Valid-51',
                            'zAddAssetAttr-Reverse Location Data-52',
                            'AAAzCldMastMedData-zOPT-53',
                            'zAddAssetAttr-Media Metadata Type-54',
                            'AAAzCldMastMedData-Data-55',
                            'CldMasterzCldMastMedData-zOPT-56',
                            'zCldMast-Media Metadata Type-57',
                            'CMzCldMastMedData-Data-58',
                            'zAsset-Bundle Scope-59',
                            'zFaceCrop-Face Area Points-60',
                            'zAsset-Face Adjustment Version-61',
                            'zAddAssetAttr-Face Regions-62',
                            'zAddAssetAttr-Face Analysis Version-63',
                            'zDetFace-Asset Visible-64',
                            'zDetFacePrint-Data-65',
                            'zPerson-Contact Matching Dictionary-66',
                            'zPerson-Face Count-67',
                            'zDetFace-Face Crop-68',
                            'zDetFace-Face Algorithm Version-69',
                            'zDetFace-Adjustment Version-70',
                            'zDetFace-UUID-71',
                            'zPerson-Person UUID-72',
                            'zDetFace-Confirmed Face Crop Generation State-73',
                            'zDetFace-Manual-74',
                            'zDetFace-Detection Type-75',
                            'zPerson-Detection Type-76',
                            'zDetFace-VIP Model Type-77',
                            'zDetFace-Name Source-78',
                            'zDetFace-Cloud Name Source-79',
                            'zPerson-Merge Candidate Confidence-80',
                            'zPerson-Person URI-81',
                            'zPerson-Display Name-82',
                            'zPerson-Full Name-83',
                            'zPerson-Cloud Verified Type-84',
                            'zFaceCrop-State-85',
                            'zFaceCrop-Type-86',
                            'zFaceCrop-Resource Data-87',
                            'zFaceCrop-UUID-88',
                            'zPerson-Type-89',
                            'zPerson-Verified Type-90',
                            'zPerson-Gender Type-91',
                            'zDetFace-Gender Type-92',
                            'zDetFace-Center X-93',
                            'zDetFace-Center Y-94',
                            'zPerson-Age Type Estimate-95',
                            'zDetFace-Age Type Estimate-96',
                            'zDetFace-Ethnicity Type-97',
                            'zDetFace-Skin Tone Type-98',
                            'zDetFace-Hair Type-99',
                            'zDetFace-Hair Color Type-100',
                            'zDetFace-Head Gear Type-101',
                            'zDetFace-Facial Hair Type-102',
                            'zDetFace-Has Face Mask-103',
                            'zDetFace-Pose Type-104',
                            'zDetFace-Face Expression Type-105',
                            'zDetFace-Has Smile-106',
                            'zDetFace-Smile Type-107',
                            'zDetFace-Lip Makeup Type-108',
                            'zDetFace-Eyes State-109',
                            'zDetFace-Is Left Eye Closed-110',
                            'zDetFace-Is Right Eye Closed-111',
                            'zDetFace-Gaze Center X-112',
                            'zDetFace-Gaze Center Y-113',
                            'zDetFace-Face Gaze Type-114',
                            'zDetFace-Eye Glasses Type-115',
                            'zDetFace-Eye Makeup Type-116',
                            'zDetFace-Cluster Squence Number Key-117',
                            'zDetFace-Grouping ID-118',
                            'zDetFace-Master ID-119',
                            'zDetFace-Quality-120',
                            'zDetFace-Quality Measure-121',
                            'zDetFace-Source Height-122',
                            'zDetFace-Source Width-123',
                            'zDetFace-Hidden/Asset Hidden-124',
                            'zDetFace-In Trash/Recently Deleted-125',
                            'zDetFace-Cloud Local State-126',
                            'zDetFace-Training Type-127',
                            'zDetFace.Pose Yaw-128',
                            'zDetFace-Body Center X-129',
                            'zDetFace-Body Center Y-130',
                            'zDetFace-Body Height-131',
                            'zDetFace-Body Width-132',
                            'zDetFace-Roll-133',
                            'zDetFace-Size-134',
                            'zDetFace-Cluster Squence Number-135',
                            'zDetFace-Blur Score-136',
                            'zDetFacePrint-Face Print Version-137',
                            'zMedAnlyAstAttr-Face Count-138',
                            'zDetFaceGroup-UUID-139',
                            'zDetFaceGroup-Person Builder State-140',
                            'zDetFaceGroup-UnNamed Face Count-141',
                            'zPerson-In Person Naming Model-142',
                            'zPerson-Key Face Pick Source Key-143',
                            'zPerson-Manual Order Key-144',
                            'zPerson-Question Type-145',
                            'zPerson-Suggested For Client Type-146',
                            'zPerson-Merge Target Person-147',
                            'zPerson-Cloud Local State-148',
                            'zFaceCrop-Cloud Local State-149',
                            'zFaceCrop-Cloud Type-150',
                            'zPerson-Cloud Delete State-151',
                            'zFaceCrop-Cloud Delete State-152',
                            'zFaceCrop-Invalid Merge Candidate Person UUID-153',
                            'zAsset-Active Library Scope Participation State-154',
                            'zAsset-zPK-155',
                            'zAddAssetAttr-zPK-156',
                            'zAsset-UUID = store.cloudphotodb-157',
                            'zAddAssetAttr-Master Fingerprint-158')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite people faces and basic asset data data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("17"):
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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZMDID AS 'zPerson - MD ID',
        CASE zPerson.ZASSETSORTORDER
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZASSETSORTORDER || ''
        END AS 'zPerson - Asset Sort Order',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',       
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSETFORFACE
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zAsset.ZFACEAREAPOINTS > 0  
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[67] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[67])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[11])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[11])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[90] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-1_FaceCropFor_' + row[86] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[90])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66],
                                personcontactmatchingdictionary,
                                row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89],
                                facecropresourcedata_blob,
                                row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                                row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
                                row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
                                row[156], row[157], row[158], row[159], row[160], row[161]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 17.'
            report = ArtifactHtmlReport('Photos.sqlite-People_Faces_Data')
            report.start_artifact_report(report_folder, 'Ph15.1-People & Faces Asset Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAddAssetAttr-Last Viewed Date-9',
                            'zAsset-Directory-Path-10',
                            'zAsset-Filename-11',
                            'zAddAssetAttr- Original Filename-12',
                            'zCldMast- Original Filename-13',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                            'zAsset- Conversation= zGenAlbum_zPK-15',
                            'zAsset-Syndication State-16',
                            'zAsset-Trashed Date-17',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-18',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-19',
                            'zAsset-Saved Asset Type-20',
                            'zAddAssetAttr-Imported by Bundle ID-21',
                            'zAddAssetAttr-Imported By Display Name-22',
                            'zAddAssetAttr-Imported by-23',
                            'zCldMast-Imported by Bundle ID-24',
                            'zCldMast-Imported by Display Name-25',
                            'zCldMast-Imported By-26',
                            'zAsset-Visibility State-27',
                            'zExtAttr-Camera Make-28',
                            'zExtAttr-Camera Model-29',
                            'zExtAttr-Lens Model-30',
                            'zAsset-Derived Camera Capture Device-31',
                            'zAddAssetAttr-Camera Captured Device-32',
                            'zAddAssetAttr-Share Type-33',
                            'zCldMast-Cloud Local State-34',
                            'zCldMast-Import Date-35',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-36',
                            'zAddAssetAttr-Import Session ID-37',
                            'zAddAssetAttr-Alt Import Image Date-38',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-39',
                            'zAsset-Cloud Batch Publish Date-40',
                            'zAsset-Cloud Server Publish Date-41',
                            'zAsset-Cloud Download Requests-42',
                            'zAsset-Cloud Batch ID-43',
                            'zAsset-Latitude-44',
                            'zExtAttr-Latitude-45',
                            'zAsset-Longitude-46',
                            'zExtAttr-Longitude-47',
                            'zAddAssetAttr-GPS Horizontal Accuracy-48',
                            'zAddAssetAttr-Location Hash-49',
                            'zAddAssetAttr-Shifted Location Valid-50',
                            'zAddAssetAttr-Shifted Location Data-51',
                            'zAddAssetAttr-Reverse Location Is Valid-52',
                            'zAddAssetAttr-Reverse Location Data-53',
                            'AAAzCldMastMedData-zOPT-54',
                            'zAddAssetAttr-Media Metadata Type-55',
                            'AAAzCldMastMedData-Data-56',
                            'CldMasterzCldMastMedData-zOPT-57',
                            'zCldMast-Media Metadata Type-58',
                            'CMzCldMastMedData-Data-59',
                            'zAsset-Bundle Scope-60',
                            'zFaceCrop-Face Area Points-61',
                            'zAsset-Face Adjustment Version-62',
                            'zAddAssetAttr-Face Regions-63',
                            'zAddAssetAttr-Face Analysis Version-64',
                            'zDetFace-Asset Visible-65',
                            'zDetFacePrint-Data-66',
                            'zPerson-Contact_Matching_Dictionary-Plist-67',
                            'zPerson-Face Count-68',
                            'zDetFace-Face Crop-69',
                            'zDetFace-Face Algorithm Version-70',
                            'zDetFace-Adjustment Version-71',
                            'zDetFace-UUID-72',
                            'zPerson-Person UUID-73',
                            'zPerson - MD ID-74',
                            'zPerson - Asset Sort Order-75',
                            'zDetFace-Confirmed Face Crop Generation State-76',
                            'zDetFace-Manual-77',
                            'zDetFace-Detection Type-78',
                            'zPerson-Detection Type-79',
                            'zDetFace-VIP Model Type-80',
                            'zDetFace-Name Source-81',
                            'zDetFace-Cloud Name Source-82',
                            'zPerson-Merge Candidate Confidence-83',
                            'zPerson-Person URI-84',
                            'zPerson-Display Name-85',
                            'zPerson-Full Name-86',
                            'zPerson-Cloud Verified Type-87',
                            'zFaceCrop-State-88',
                            'zFaceCrop-Type-89',
                            'zFaceCrop-Resource Data-90',
                            'zFaceCrop-UUID-91',
                            'zPerson-Type-92',
                            'zPerson-Verified Type-93',
                            'zPerson-Gender Type-94',
                            'zDetFace-Gender Type-95',
                            'zDetFace-Center X-96',
                            'zDetFace-Center Y-97',
                            'zPerson-Age Type Estimate-98',
                            'zDetFace-Age Type Estimate-99',
                            'zDetFace-Ethnicity Type-100',
                            'zDetFace-Skin Tone Type-101',
                            'zDetFace-Hair Type-102',
                            'zDetFace-Hair Color Type-103',
                            'zDetFace-Head Gear Type-104',
                            'zDetFace-Facial Hair Type-105',
                            'zDetFace-Has Face Mask-106',
                            'zDetFace-Pose Type-107',
                            'zDetFace-Face Expression Type-108',
                            'zDetFace-Has Smile-109',
                            'zDetFace-Smile Type-110',
                            'zDetFace-Lip Makeup Type-111',
                            'zDetFace-Eyes State-112',
                            'zDetFace-Is Left Eye Closed-113',
                            'zDetFace-Is Right Eye Closed-114',
                            'zDetFace-Gaze Center X-115',
                            'zDetFace-Gaze Center Y-116',
                            'zDetFace-Face Gaze Type-117',
                            'zDetFace-Eye Glasses Type-118',
                            'zDetFace-Eye Makeup Type-119',
                            'zDetFace-Cluster Squence Number Key-120',
                            'zDetFace-Grouping ID-121',
                            'zDetFace-Master ID-122',
                            'zDetFace-Quality-123',
                            'zDetFace-Quality Measure-124',
                            'zDetFace-Source Height-125',
                            'zDetFace-Source Width-126',
                            'zDetFace-Hidden/Asset Hidden-127',
                            'zDetFace-In Trash/Recently Deleted-128',
                            'zDetFace-Cloud Local State-129',
                            'zDetFace-Training Type-130',
                            'zDetFace.Pose Yaw-131',
                            'zDetFace-Body Center X-132',
                            'zDetFace-Body Center Y-133',
                            'zDetFace-Body Height-134',
                            'zDetFace-Body Width-135',
                            'zDetFace-Roll-136',
                            'zDetFace-Size-137',
                            'zDetFace-Cluster Squence Number-138',
                            'zDetFace-Blur Score-139',
                            'zDetFacePrint-Face Print Version-140',
                            'zMedAnlyAstAttr-Face Count-141',
                            'zDetFaceGroup-UUID-142',
                            'zDetFaceGroup-Person Builder State-143',
                            'zDetFaceGroup-UnNamed Face Count-144',
                            'zPerson-In Person Naming Model-145',
                            'zPerson-Key Face Pick Source Key-146',
                            'zPerson-Manual Order Key-147',
                            'zPerson-Question Type-148',
                            'zPerson-Suggested For Client Type-149',
                            'zPerson-Merge Target Person-150',
                            'zPerson-Cloud Local State-151',
                            'zFaceCrop-Cloud Local State-152',
                            'zFaceCrop-Cloud Type-153',
                            'zPerson-Cloud Delete State-154',
                            'zFaceCrop-Cloud Delete State-155',
                            'zFaceCrop-Invalid Merge Canidate Person UUID-156',
                            'zAsset-Active Library Scope Participation State-157',
                            'zAsset-zPK-158',
                            'zAddAssetAttr-zPK-159',
                            'zAsset-UUID = store.cloudphotodb-160',
                            'zAddAssetAttr-Master Fingerprint-161')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.1-People & Faces Asset Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite people faces and basic asset data data')

        db.close()
        return


def get_ph15assetpeopledetfacesyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for Syndication.photoslibrary-database-Photos.sqlite basic asset people and face data iOS " + iosversion)
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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',        
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zAsset.ZFACEAREAPOINTS > 0      
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[60] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[60])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[10])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[78] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_FaceCropFor_' + row[74] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[78])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59],
                                  personcontactmatchingdictionary,
                                  row[61], row[62], row[63],
                                  row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                  row[73], row[74], row[75], row[76], row[77],
                                  facecropresourcedata_blob,
                                  row[79], row[80], row[81],
                                  row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                                  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                  row[132], row[133], row[134]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 14.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph15.2-People & Faces Asset Data-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAsset-Trashed Date-13',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                            'zAsset-Saved Asset Type-15',
                            'zAddAssetAttr-Creator Bundle ID-16',
                            'zAddAssetAttr-Imported By Display Name-17',
                            'zAddAssetAttr-Imported by-18',
                            'zCldMast-Imported by Bundle ID-19',
                            'zCldMast-Imported by Display Name-20',
                            'zCldMast-Imported By-21',
                            'zAsset-Visibility State-22',
                            'zExtAttr-Camera Make-23',
                            'zExtAttr-Camera Model-24',
                            'zExtAttr-Lens Model-25',
                            'zAsset-Derived Camera Capture Device-26',
                            'zAddAssetAttr-Camera Captured Device-27',
                            'zAddAssetAttr-Share Type-28',
                            'zCldMast-Cloud Local State-29',
                            'zCldMast-Import Date-30',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-31',
                            'zAddAssetAttr-Import Session ID-32',
                            'zAddAssetAttr-Alt Import Image Date-33',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-34',
                            'zAsset-Cloud Batch Publish Date-35',
                            'zAsset-Cloud Server Publish Date-36',
                            'zAsset-Cloud Download Requests-37',
                            'zAsset-Cloud Batch ID-38',
                            'zAsset-Latitude-39',
                            'zExtAttr-Latitude-40',
                            'zAsset-Longitude-41',
                            'zExtAttr-Longitude-42',
                            'zAddAssetAttr-GPS Horizontal Accuracy-43',
                            'zAddAssetAttr-Location Hash-44',
                            'zAddAssetAttr-Shifted Location Valid-45',
                            'zAddAssetAttr-Shifted Location Data-46',
                            'zAddAssetAttr-Reverse Location Is Valid-47',
                            'zAddAssetAttr-Reverse Location Data-48',
                            'AAAzCldMastMedData-zOPT-49',
                            'zAddAssetAttr-Media Metadata Type-50',
                            'AAAzCldMastMedData-Data-51',
                            'CldMasterzCldMastMedData-zOPT-52',
                            'zCldMast-Media Metadata Type-53',
                            'CMzCldMastMedData-Data-54',
                            'zFaceCrop-Face Area Points-55',
                            'zAsset-Face Adjustment Version-56',
                            'zAddAssetAttr-Face Regions-57',
                            'zDetFace-Asset Visible-58',
                            'zDetFacePrint-Data-59',
                            'zPerson-Contact Matching Dictionary-60',
                            'zPerson-Face Count-61',
                            'zDetFace-Face Crop-62',
                            'zDetFace-Face Algorithm Version-63',
                            'zDetFace-Adjustment Version-64',
                            'zDetFace-UUID-65',
                            'zPerson-Person UUID-66',
                            'zDetFace-Confirmed Face Crop Generation State-67',
                            'zDetFace-Manual-68',
                            'zDetFace-VIP Model Type-69',
                            'zDetFace-Name Source-70',
                            'zDetFace-Cloud Name Source-71',
                            'zPerson-Person URI-72',
                            'zPerson-Display Name-73',
                            'zPerson-Full Name-74',
                            'zPerson-Cloud Verified Type-75',
                            'zFaceCrop-State-76',
                            'zFaceCrop-Type-77',
                            'zFaceCrop-Resource Data-78',
                            'zFaceCrop-UUID-79',
                            'zPerson-Type-80',
                            'zPerson-Verified Type-81',
                            'zPerson-Gender Type-82',
                            'zDetFace-Gender Type-83',
                            'zDetFace-Center X-84',
                            'zDetFace-Center Y-85',
                            'zPerson-Age Type Estimate-86',
                            'zDetFace-Age Type Estimate-87',
                            'zDetFace-Hair Color Type-88',
                            'zDetFace-Facial Hair Type-89',
                            'zDetFace-Has Smile-90',
                            'zDetFace-Smile Type-91',
                            'zDetFace-Lip Makeup Type-92',
                            'zDetFace-Eyes State-93',
                            'zDetFace-Is Left Eye Closed-94',
                            'zDetFace-Is Right Eye Closed-95',
                            'zDetFace-Eye Glasses Type-96',
                            'zDetFace-Eye Makeup Type-97',
                            'zDetFace-Cluster Squence Number Key-98',
                            'zDetFace-Grouping ID-99',
                            'zDetFace-Master ID-100',
                            'zDetFace-Quality-101',
                            'zDetFace-Quality Measure-102',
                            'zDetFace-Source Height-103',
                            'zDetFace-Source Width-104',
                            'zDetFace-Hidden/Asset Hidden-105',
                            'zDetFace-In Trash/Recently Deleted-106',
                            'zDetFace-Cloud Local State-107',
                            'zDetFace-Training Type-108',
                            'zDetFace.Pose Yaw-109',
                            'zDetFace-Roll-110',
                            'zDetFace-Size-111',
                            'zDetFace-Cluster Squence Number-112',
                            'zDetFace-Blur Score-113',
                            'zDetFacePrint-Face Print Version-114',
                            'zMedAnlyAstAttr-Face Count-115',
                            'zDetFaceGroup-UUID-116',
                            'zDetFaceGroup-Person Builder State-117',
                            'zDetFaceGroup-UnNamed Face Count-118',
                            'zPerson-In Person Naming Model-119',
                            'zPerson-Key Face Pick Source Key-120',
                            'zPerson-Manual Order Key-121',
                            'zPerson-Question Type-122',
                            'zPerson-Suggested For Client Type-123',
                            'zPerson-Merge Target Person-124',
                            'zPerson-Cloud Local State-125',
                            'zFaceCrop-Cloud Local State-126',
                            'zFaceCrop-Cloud Type-127',
                            'zPerson-Cloud Delete State-128',
                            'zFaceCrop-Cloud Delete State-129',
                            'zFaceCrop-Invalid Merge Candidate Person UUID-130',
                            'zAsset-zPK-131',
                            'zAddAssetAttr-zPK-132',
                            'zAsset-UUID = store.cloudphotodb-133',
                            'zAddAssetAttr-Master Fingerprint-134')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.2-People & Faces Asset Data-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.2-People & Faces Asset Data-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite people faces and basic asset data data')

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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP       
        WHERE zAsset.ZFACEAREAPOINTS > 0  
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[65] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[65])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[10])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[85] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_FaceCropFor_' + row[81] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[85])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64],
                                  personcontactmatchingdictionary,
                                  row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                  row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                  row[82], row[83], row[84],
                                  facecropresourcedata_blob,
                                  row[86], row[87], row[88], row[89], row[90],
                                  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                                  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
                                  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 15.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph15.2-People & Faces Asset Data-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                            'zAsset- Conversation= zGenAlbum_zPK -14',
                            'zAsset-Syndication State-15',
                            'zAsset-Trashed Date-16',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-17',
                            'zAsset-Saved Asset Type-18',
                            'zAddAssetAttr-Imported by Bundle ID-19',
                            'zAddAssetAttr-Imported By Display Name-20',
                            'zAddAssetAttr-Imported by-21',
                            'zCldMast-Imported by Bundle ID-22',
                            'zCldMast-Imported by Display Name-23',
                            'zCldMast-Imported By-24',
                            'zAsset-Visibility State-25',
                            'zExtAttr-Camera Make-26',
                            'zExtAttr-Camera Model-27',
                            'zExtAttr-Lens Model-28',
                            'zAsset-Derived Camera Capture Device-29',
                            'zAddAssetAttr-Camera Captured Device-30',
                            'zAddAssetAttr-Share Type-31',
                            'zCldMast-Cloud Local State-32',
                            'zCldMast-Import Date-33',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-34',
                            'zAddAssetAttr-Import Session ID-35',
                            'zAddAssetAttr-Alt Import Image Date-36',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-37',
                            'zAsset-Cloud Batch Publish Date-38',
                            'zAsset-Cloud Server Publish Date-39',
                            'zAsset-Cloud Download Requests-40',
                            'zAsset-Cloud Batch ID-41',
                            'zAsset-Latitude-42',
                            'zExtAttr-Latitude-43',
                            'zAsset-Longitude-44',
                            'zExtAttr-Longitude-45',
                            'zAddAssetAttr-GPS Horizontal Accuracy-46',
                            'zAddAssetAttr-Location Hash-47',
                            'zAddAssetAttr-Shifted Location Valid-48',
                            'zAddAssetAttr-Shifted Location Data-49',
                            'zAddAssetAttr-Reverse Location Is Valid-50',
                            'zAddAssetAttr-Reverse Location Data-51',
                            'AAAzCldMastMedData-zOPT-52',
                            'zAddAssetAttr-Media Metadata Type-53',
                            'AAAzCldMastMedData-Data-54',
                            'CldMasterzCldMastMedData-zOPT-55',
                            'zCldMast-Media Metadata Type-56',
                            'CMzCldMastMedData-Data-57',
                            'zAsset-Bundle Scope-58',
                            'zFaceCrop-Face Area Points-59',
                            'zAsset-Face Adjustment Version-60',
                            'zAddAssetAttr-Face Regions-61',
                            'zAddAssetAttr-Face Analysis Version-62',
                            'zDetFace-Asset Visible-63',
                            'zDetFacePrint-Data-64',
                            'zPerson-Contact Matching Dictionary-65',
                            'zPerson-Face Count-66',
                            'zDetFace-Face Crop-67',
                            'zDetFace-Face Algorithm Version-68',
                            'zDetFace-Adjustment Version-69',
                            'zDetFace-UUID-70',
                            'zPerson-Person UUID-71',
                            'zDetFace-Confirmed Face Crop Generation State-72',
                            'zDetFace-Manual-73',
                            'zDetFace-Detection Type-74',
                            'zPerson-Detection Type-75',
                            'zDetFace-VIP Model Type-76',
                            'zDetFace-Name Source-77',
                            'zDetFace-Cloud Name Source-78',
                            'zPerson-Person URI-79',
                            'zPerson-Display Name-80',
                            'zPerson-Full Name-81',
                            'zPerson-Cloud Verified Type-82',
                            'zFaceCrop-State-83',
                            'zFaceCrop-Type-84',
                            'zFaceCrop-Resource Data-85',
                            'zFaceCrop-UUID-86',
                            'zPerson-Type-87',
                            'zPerson-Verified Type-88',
                            'zPerson-Gender Type-89',
                            'zDetFace-Gender Type-90',
                            'zDetFace-Center X-91',
                            'zDetFace-Center Y-92',
                            'zPerson-Age Type Estimate-93',
                            'zDetFace-Age Type Estimate-94',
                            'zDetFace-Ethnicity Type-95',
                            'zDetFace-Skin Tone Type-96',
                            'zDetFace-Hair Type-97',
                            'zDetFace-Hair Color Type-98',
                            'zDetFace-Head Gear Type-99',
                            'zDetFace-Facial Hair Type-100',
                            'zDetFace-Has Face Mask-101',
                            'zDetFace-Pose Type-102',
                            'zDetFace-Face Expression Type-103',
                            'zDetFace-Has Smile-104',
                            'zDetFace-Smile Type-105',
                            'zDetFace-Lip Makeup Type-106',
                            'zDetFace-Eyes State-107',
                            'zDetFace-Is Left Eye Closed-108',
                            'zDetFace-Is Right Eye Closed-109',
                            'zDetFace-Gaze Center X-110',
                            'zDetFace-Gaze Center Y-111',
                            'zDetFace-Face Gaze Type-112',
                            'zDetFace-Eye Glasses Type-113',
                            'zDetFace-Eye Makeup Type-114',
                            'zDetFace-Cluster Squence Number Key-115',
                            'zDetFace-Grouping ID-116',
                            'zDetFace-Master ID-117',
                            'zDetFace-Quality-118',
                            'zDetFace-Quality Measure-119',
                            'zDetFace-Source Height-120',
                            'zDetFace-Source Width-121',
                            'zDetFace-Hidden/Asset Hidden-122',
                            'zDetFace-In Trash/Recently Deleted-123',
                            'zDetFace-Cloud Local State-124',
                            'zDetFace-Training Type-125',
                            'zDetFace.Pose Yaw-126',
                            'zDetFace-Body Center X-127',
                            'zDetFace-Body Center Y-128',
                            'zDetFace-Body Height-129',
                            'zDetFace-Body Width-130',
                            'zDetFace-Roll-131',
                            'zDetFace-Size-132',
                            'zDetFace-Cluster Squence Number-133',
                            'zDetFace-Blur Score-134',
                            'zDetFacePrint-Face Print Version-135',
                            'zMedAnlyAstAttr-Face Count-136',
                            'zDetFaceGroup-UUID-137',
                            'zDetFaceGroup-Person Builder State-138',
                            'zDetFaceGroup-UnNamed Face Count-139',
                            'zPerson-In Person Naming Model-140',
                            'zPerson-Key Face Pick Source Key-141',
                            'zPerson-Manual Order Key-142',
                            'zPerson-Question Type-143',
                            'zPerson-Suggested For Client Type-144',
                            'zPerson-Merge Target Person-145',
                            'zPerson-Cloud Local State-146',
                            'zFaceCrop-Cloud Local State-147',
                            'zFaceCrop-Cloud Type-148',
                            'zPerson-Cloud Delete State-149',
                            'zFaceCrop-Cloud Delete State-150',
                            'zFaceCrop-Invalid Merge Canidate Person UUID-151',
                            'zAsset-zPK-152',
                            'zAddAssetAttr-zPK-153',
                            'zAsset-UUID = store.cloudphotodb-154',
                            'zAddAssetAttr-Master Fingerprint-155')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.2-People & Faces Asset Data-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.2-People & Faces Asset Data-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite people faces and basic asset data data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Candidate Person UUID',       
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zAsset.ZFACEAREAPOINTS > 0  
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[66] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[66])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[10])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[10])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[87] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_FaceCropFor_' + row[83] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[87])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65],
                                  personcontactmatchingdictionary,
                                  row[67], row[68], row[69], row[70], row[71], row[72],
                                  row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                  row[82], row[83], row[84], row[85], row[86],
                                  facecropresourcedata_blob,
                                  row[88], row[89], row[90],
                                  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                                  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
                                  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
                                  row[156], row[157], row[158]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 16.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph15.2-People & Faces Asset Data-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                            'zAsset- Conversation= zGenAlbum_zPK-14',
                            'zAsset-Syndication State-15',
                            'zAsset-Trashed Date-16',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-17',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-18',
                            'zAsset-Saved Asset Type-19',
                            'zAddAssetAttr-Imported by Bundle ID-20',
                            'zAddAssetAttr-Imported By Display Name-21',
                            'zAddAssetAttr-Imported by-22',
                            'zCldMast-Imported by Bundle ID-23',
                            'zCldMast-Imported by Display Name-24',
                            'zCldMast-Imported By-25',
                            'zAsset-Visibility State-26',
                            'zExtAttr-Camera Make-27',
                            'zExtAttr-Camera Model-28',
                            'zExtAttr-Lens Model-29',
                            'zAsset-Derived Camera Capture Device-30',
                            'zAddAssetAttr-Camera Captured Device-31',
                            'zAddAssetAttr-Share Type-32',
                            'zCldMast-Cloud Local State-33',
                            'zCldMast-Import Date-34',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-35',
                            'zAddAssetAttr-Import Session ID-36',
                            'zAddAssetAttr-Alt Import Image Date-37',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-38',
                            'zAsset-Cloud Batch Publish Date-39',
                            'zAsset-Cloud Server Publish Date-40',
                            'zAsset-Cloud Download Requests-41',
                            'zAsset-Cloud Batch ID-42',
                            'zAsset-Latitude-43',
                            'zExtAttr-Latitude-44',
                            'zAsset-Longitude-45',
                            'zExtAttr-Longitude-46',
                            'zAddAssetAttr-GPS Horizontal Accuracy-47',
                            'zAddAssetAttr-Location Hash-48',
                            'zAddAssetAttr-Shifted Location Valid-49',
                            'zAddAssetAttr-Shifted Location Data-50',
                            'zAddAssetAttr-Reverse Location Is Valid-51',
                            'zAddAssetAttr-Reverse Location Data-52',
                            'AAAzCldMastMedData-zOPT-53',
                            'zAddAssetAttr-Media Metadata Type-54',
                            'AAAzCldMastMedData-Data-55',
                            'CldMasterzCldMastMedData-zOPT-56',
                            'zCldMast-Media Metadata Type-57',
                            'CMzCldMastMedData-Data-58',
                            'zAsset-Bundle Scope-59',
                            'zFaceCrop-Face Area Points-60',
                            'zAsset-Face Adjustment Version-61',
                            'zAddAssetAttr-Face Regions-62',
                            'zAddAssetAttr-Face Analysis Version-63',
                            'zDetFace-Asset Visible-64',
                            'zDetFacePrint-Data-65',
                            'zPerson-Contact Matching Dictionary-66',
                            'zPerson-Face Count-67',
                            'zDetFace-Face Crop-68',
                            'zDetFace-Face Algorithm Version-69',
                            'zDetFace-Adjustment Version-70',
                            'zDetFace-UUID-71',
                            'zPerson-Person UUID-72',
                            'zDetFace-Confirmed Face Crop Generation State-73',
                            'zDetFace-Manual-74',
                            'zDetFace-Detection Type-75',
                            'zPerson-Detection Type-76',
                            'zDetFace-VIP Model Type-77',
                            'zDetFace-Name Source-78',
                            'zDetFace-Cloud Name Source-79',
                            'zPerson-Merge Candidate Confidence-80',
                            'zPerson-Person URI-81',
                            'zPerson-Display Name-82',
                            'zPerson-Full Name-83',
                            'zPerson-Cloud Verified Type-84',
                            'zFaceCrop-State-85',
                            'zFaceCrop-Type-86',
                            'zFaceCrop-Resource Data-87',
                            'zFaceCrop-UUID-88',
                            'zPerson-Type-89',
                            'zPerson-Verified Type-90',
                            'zPerson-Gender Type-91',
                            'zDetFace-Gender Type-92',
                            'zDetFace-Center X-93',
                            'zDetFace-Center Y-94',
                            'zPerson-Age Type Estimate-95',
                            'zDetFace-Age Type Estimate-96',
                            'zDetFace-Ethnicity Type-97',
                            'zDetFace-Skin Tone Type-98',
                            'zDetFace-Hair Type-99',
                            'zDetFace-Hair Color Type-100',
                            'zDetFace-Head Gear Type-101',
                            'zDetFace-Facial Hair Type-102',
                            'zDetFace-Has Face Mask-103',
                            'zDetFace-Pose Type-104',
                            'zDetFace-Face Expression Type-105',
                            'zDetFace-Has Smile-106',
                            'zDetFace-Smile Type-107',
                            'zDetFace-Lip Makeup Type-108',
                            'zDetFace-Eyes State-109',
                            'zDetFace-Is Left Eye Closed-110',
                            'zDetFace-Is Right Eye Closed-111',
                            'zDetFace-Gaze Center X-112',
                            'zDetFace-Gaze Center Y-113',
                            'zDetFace-Face Gaze Type-114',
                            'zDetFace-Eye Glasses Type-115',
                            'zDetFace-Eye Makeup Type-116',
                            'zDetFace-Cluster Squence Number Key-117',
                            'zDetFace-Grouping ID-118',
                            'zDetFace-Master ID-119',
                            'zDetFace-Quality-120',
                            'zDetFace-Quality Measure-121',
                            'zDetFace-Source Height-122',
                            'zDetFace-Source Width-123',
                            'zDetFace-Hidden/Asset Hidden-124',
                            'zDetFace-In Trash/Recently Deleted-125',
                            'zDetFace-Cloud Local State-126',
                            'zDetFace-Training Type-127',
                            'zDetFace.Pose Yaw-128',
                            'zDetFace-Body Center X-129',
                            'zDetFace-Body Center Y-130',
                            'zDetFace-Body Height-131',
                            'zDetFace-Body Width-132',
                            'zDetFace-Roll-133',
                            'zDetFace-Size-134',
                            'zDetFace-Cluster Squence Number-135',
                            'zDetFace-Blur Score-136',
                            'zDetFacePrint-Face Print Version-137',
                            'zMedAnlyAstAttr-Face Count-138',
                            'zDetFaceGroup-UUID-139',
                            'zDetFaceGroup-Person Builder State-140',
                            'zDetFaceGroup-UnNamed Face Count-141',
                            'zPerson-In Person Naming Model-142',
                            'zPerson-Key Face Pick Source Key-143',
                            'zPerson-Manual Order Key-144',
                            'zPerson-Question Type-145',
                            'zPerson-Suggested For Client Type-146',
                            'zPerson-Merge Target Person-147',
                            'zPerson-Cloud Local State-148',
                            'zFaceCrop-Cloud Local State-149',
                            'zFaceCrop-Cloud Type-150',
                            'zPerson-Cloud Delete State-151',
                            'zFaceCrop-Cloud Delete State-152',
                            'zFaceCrop-Invalid Merge Candidate Person UUID-153',
                            'zAsset-Active Library Scope Participation State-154',
                            'zAsset-zPK-155',
                            'zAddAssetAttr-zPK-156',
                            'zAsset-UUID = store.cloudphotodb-157',
                            'zAddAssetAttr-Master Fingerprint-158')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.2-People & Faces Asset Data-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.2-People & Faces Asset Data-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite people faces and basic asset data data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("17"):
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
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
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
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
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
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE
            WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
            ELSE 'Face Area Points Not Detected in zAsset'
        END AS 'zFaceCrop-Face Area Points',
        zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
        CASE
            WHEN zAddAssetAttr.ZFACEREGIONS > 0 THEN 'zAddAssetAttr-Face_Regions_has_Data'
            ELSE 'zAddAssetAttr-Face_Regions_has_NO-Data'
        END AS 'zAddAssetAttr-Face_Regions-SeeRawDBData',
        zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
        CASE zDetFace.ZASSETVISIBLE
            WHEN 0 THEN 'Asset Not Visible Photo Library-0'
            WHEN 1 THEN 'Asset Visible Photo Library-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
        END AS 'zDetFace-Asset Visible',
        CASE
            WHEN zDetFacePrint.ZDATA > 0 THEN 'zDetFacePrint-Data_has_Data'
            ELSE 'zDetFacePrint-Data_NO-Data'
        END AS 'zDetFacePrint-Data-SeeRawDBData',
        zPerson.ZCONTACTMATCHINGDICTIONARY AS 'zPerson-Contact Matching Dictionary',
        zPerson.ZFACECOUNT AS 'zPerson-Face Count',
        zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
        zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
        zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
        zDetFace.ZUUID AS 'zDetFace-UUID',
        zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
        zPerson.ZMDID AS 'zPerson - MD ID',
        CASE zPerson.ZASSETSORTORDER
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZASSETSORTORDER || ''
        END AS 'zPerson - Asset Sort Order',
        CASE zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCONFIRMEDFACECROPGENERATIONSTATE || ''
        END AS 'zDetFace-Confirmed Face Crop Generation State',
        CASE zDetFace.ZMANUAL
            WHEN 0 THEN 'zDetFace-Auto Detected-0'
            WHEN 1 THEN 'zDetFace-Manually Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZMANUAL || ''
        END AS 'zDetFace-Manual',
        CASE zDetFace.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZDETECTIONTYPE || ''
        END AS 'zDetFace-Detection Type',
        CASE zPerson.ZDETECTIONTYPE
            WHEN 1 THEN '1-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZDETECTIONTYPE || ''
        END AS 'zPerson-Detection Type',
        CASE zDetFace.ZVIPMODELTYPE
            WHEN 0 THEN 'Not VIP-0'
            WHEN 1 THEN 'VIP-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZVIPMODELTYPE || ''
        END AS 'zDetFace-VIP Model Type',
        CASE zDetFace.ZNAMESOURCE
            WHEN 0 THEN 'No Name Listed-0'
            WHEN 1 THEN '1-Face Crop-1'
            WHEN 2 THEN '2-Verified/Has-Person-URI'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZNAMESOURCE || ''
        END AS 'zDetFace-Name Source',
        CASE zDetFace.ZCLOUDNAMESOURCE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN '1-User Added Via Face Crop-1'
            WHEN 5 THEN '5-Asset Shared has Name'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDNAMESOURCE || ''
        END AS 'zDetFace-Cloud Name Source',
        zPerson.ZMERGECANDIDATECONFIDENCE AS 'zPerson-Merge Candidate Confidence',
        zPerson.ZPERSONURI AS 'zPerson-Person URI',
        zPerson.ZDISPLAYNAME AS 'zPerson-Display Name',
        zPerson.ZFULLNAME AS 'zPerson-Full Name',
        CASE zPerson.ZCLOUDVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDVERIFIEDTYPE || ''
        END AS 'zPerson-Cloud Verified Type',
        CASE zFaceCrop.ZSTATE
            WHEN 5 THEN 'Validated-5'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZSTATE || ''
        END AS 'zFaceCrop-State',
        CASE zFaceCrop.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-Active'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZTYPE || ''
        END AS 'zFaceCrop-Type',
        zFaceCrop.ZRESOURCEDATA AS 'zFaceCrop-Resource Data',
        zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
        CASE zPerson.ZTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZTYPE || ''
        END AS 'zPerson-Type',
        CASE zPerson.ZVERIFIEDTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZVERIFIEDTYPE || ''
        END AS 'zPerson-Verified Type',
        CASE zPerson.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZGENDERTYPE || ''
        END AS 'zPerson-Gender Type',
        CASE zDetFace.ZGENDERTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Male-1'
            WHEN 2 THEN 'Female-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGENDERTYPE || ''
        END AS 'zDetFace-Gender Type',
        zDetFace.ZCENTERX AS 'zDetFace-Center X',
        zDetFace.ZCENTERY AS 'zDetFace-Center Y',
        CASE zPerson.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
        END AS 'zPerson-Age Type Estimate',
        CASE zDetFace.ZAGETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Infant/Toddler Age Type-1'
            WHEN 2 THEN 'Toddler/Child Age Type-2'
            WHEN 3 THEN 'Child/Young Adult Age Type-3'
            WHEN 4 THEN 'Young Adult/Adult Age Type-4'
            WHEN 5 THEN 'Adult-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
        END AS 'zDetFace-Age Type Estimate',
        CASE zDetFace.ZETHNICITYTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/African American-1'
            WHEN 2 THEN 'White-2'
            WHEN 3 THEN 'Hispanic/Latino-3'
            WHEN 4 THEN 'Asian-4'
            WHEN 5 THEN 'Native Hawaiian/Other Pacific Islander-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZETHNICITYTYPE || ''
        END AS 'zDetFace-Ethnicity Type',
        CASE zDetFace.ZSKINTONETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Light-Pale White Skin Tone-1'
            WHEN 2 THEN 'White-Fair Skin Tone-2'
            WHEN 3 THEN 'Medium-White to Olive Skin Tone-3'
            WHEN 4 THEN 'Olive-Moderate Brown Skin Tone-4'
            WHEN 5 THEN 'Brown-Dark Brown Skin Tone-5'
            WHEN 6 THEN 'Black-Very Dark Brown to Black Skin Tone-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSKINTONETYPE || ''
        END AS 'zDetFace-Skin Tone Type',
        CASE zDetFace.ZHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            WHEN 6 THEN '6-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRTYPE || ''
        END AS 'zDetFace-Hair Type',
        CASE zDetFace.ZHAIRCOLORTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Black/Brown Hair Color-1'
            WHEN 2 THEN 'Brown/Blonde Hair Color-2'
            WHEN 3 THEN 'Brown/Red Hair Color-3'
            WHEN 4 THEN 'Red/White Hair Color-4'
            WHEN 5 THEN 'StillTesting/Artifical-5'
            WHEN 6 THEN 'White/Bald Hair Color-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHAIRCOLORTYPE || ''
        END AS 'zDetFace-Hair Color Type',
        CASE zDetFace.ZHEADGEARTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-No Headgear'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHEADGEARTYPE || ''
        END AS 'zDetFace-Head Gear Type',
        CASE zDetFace.ZFACIALHAIRTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Clean Shaven Facial Hair Type-1'
            WHEN 2 THEN 'Beard Facial Hair Type-2'
            WHEN 3 THEN 'Goatee Facial Hair Type-3'
            WHEN 4 THEN 'Mustache Facial Hair Type-4'
            WHEN 5 THEN 'Stubble Facial Hair Type-5'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACIALHAIRTYPE || ''
        END AS 'zDetFace-Facial Hair Type',
        CASE zDetFace.ZHASFACEMASK
            WHEN 0 THEN 'No Mask-0'
            WHEN 1 THEN 'Has Mask-1'
            WHEN 2 THEN '2-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASFACEMASK || ''
        END AS 'zDetFace-Has Face Mask',
        CASE zDetFace.ZPOSETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Face Frontal Pose-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN 'Face Profile Pose-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZPOSETYPE || ''
        END AS 'zDetFace-Pose Type',
        CASE zDetFace.ZFACEEXPRESSIONTYPE
            WHEN 0 THEN 'NA-0'
            WHEN 1 THEN 'Disgusted/Angry-1'
            WHEN 2 THEN 'Suprised/Fearful-2'
            WHEN 3 THEN 'Neutral-3'
            WHEN 4 THEN 'Confident/Smirk-4'
            WHEN 5 THEN 'Happiness-5'
            WHEN 6 THEN 'Sadness-6'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZFACEEXPRESSIONTYPE || ''
        END AS 'zDetFace-Face Expression Type',
        CASE zDetFace.ZHASSMILE
            WHEN 0 THEN 'zDetFace No Smile-0'
            WHEN 1 THEN 'zDetFace Smile-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHASSMILE || ''
        END AS 'zDetFace-Has Smile',
        CASE zDetFace.ZSMILETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'zDetFace Smile No Teeth-1'
            WHEN 2 THEN 'zDetFace Smile has Teeth-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZSMILETYPE || ''
        END AS 'zDetFace-Smile Type',
        CASE zDetFace.ZLIPMAKEUPTYPE
            WHEN 0 THEN 'zDetFace No Lip Makeup-0'
            WHEN 1 THEN 'zDetFace Lip Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZLIPMAKEUPTYPE || ''
        END AS 'zDetFace-Lip Makeup Type',
        CASE zDetFace.ZEYESSTATE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eyes Closed-1'
            WHEN 2 THEN 'Eyes Open-2'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYESSTATE || ''
        END AS 'zDetFace-Eyes State',
        CASE zDetFace.ZISLEFTEYECLOSED
            WHEN 0 THEN 'Left Eye Open-0'
            WHEN 1 THEN 'Left Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISLEFTEYECLOSED || ''
        END AS 'zDetFace-Is Left Eye Closed',
        CASE zDetFace.ZISRIGHTEYECLOSED
            WHEN 0 THEN 'Right Eye Open-0'
            WHEN 1 THEN 'Right Eye Closed-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISRIGHTEYECLOSED || ''
        END AS 'zDetFace-Is Right Eye Closed',
        zDetFace.ZGAZECENTERX AS 'zDetFace-Gaze Center X',
        zDetFace.ZGAZECENTERY AS 'zDetFace-Gaze Center Y',
        CASE zDetFace.ZGAZETYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGAZETYPE || ''
        END AS 'zDetFace-Face Gaze Type',
        CASE zDetFace.ZGLASSESTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN 'Eye Glasses-1'
            WHEN 2 THEN 'Sun Glasses-2'
            WHEN 3 THEN 'No Glasses-3'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZGLASSESTYPE || ''
        END AS 'zDetFace-Eye Glasses Type',
        CASE zDetFace.ZEYEMAKEUPTYPE
            WHEN 0 THEN 'No Eye Makeup-0'
            WHEN 1 THEN 'Eye Makeup Detected-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZEYEMAKEUPTYPE || ''
        END AS 'zDetFace-Eye Makeup Type',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number Key',
        zDetFace.ZGROUPINGIDENTIFIER AS 'zDetFace-Grouping ID',
        zDetFace.ZMASTERIDENTIFIER AS 'zDetFace-Master ID',
        zDetFace.ZQUALITY AS 'zDetFace-Quality',
        zDetFace.ZQUALITYMEASURE AS 'zDetFace-Quality Measure',
        zDetFace.ZSOURCEHEIGHT AS 'zDetFace-Source Height',
        zDetFace.ZSOURCEWIDTH AS 'zDetFace-Source Width',
        CASE zDetFace.ZHIDDEN
            WHEN 0 THEN 'Not Hidden-0'
            WHEN 1 THEN 'Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZHIDDEN || ''
        END AS 'zDetFace-Hidden/Asset Hidden',
        CASE zDetFace.ZISINTRASH
            WHEN 0 THEN 'Not In Trash-0'
            WHEN 1 THEN 'In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
        END AS 'zDetFace-In Trash/Recently Deleted',
        CASE zDetFace.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZCLOUDLOCALSTATE || ''
        END AS 'zDetFace-Cloud Local State',
        CASE zDetFace.ZTRAININGTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zDetFace.ZTRAININGTYPE
        END AS 'zDetFace-Training Type',
        zDetFace.ZPOSEYAW AS 'zDetFace.Pose Yaw',
        zDetFace.ZBODYCENTERX AS 'zDetFace-Body Center X',
        zDetFace.ZBODYCENTERY AS 'zDetFace-Body Center Y',
        zDetFace.ZBODYHEIGHT AS 'zDetFace-Body Height',
        zDetFace.ZBODYWIDTH AS 'zDetFace-Body Width',
        zDetFace.ZROLL AS 'zDetFace-Roll',
        zDetFace.ZSIZE AS 'zDetFace-Size',
        zDetFace.ZCLUSTERSEQUENCENUMBER AS 'zDetFace-Cluster Squence Number',
        zDetFace.ZBLURSCORE AS 'zDetFace-Blur Score',
        zDetFacePrint.ZFACEPRINTVERSION AS 'zDetFacePrint-Face Print Version',
        zMedAnlyAstAttr.ZFACECOUNT AS 'zMedAnlyAstAttr-Face Count',
        zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
        zDetFaceGroup.ZPERSONBUILDERSTATE AS 'zDetFaceGroup-Person Builder State',
        zDetFaceGroup.ZUNNAMEDFACECOUNT AS 'zDetFaceGroup-UnNamed Face Count',
        zPerson.ZINPERSONNAMINGMODEL AS 'zPerson-In Person Naming Model',
        zPerson.ZKEYFACEPICKSOURCE AS 'zPerson-Key Face Pick Source Key',
        zPerson.ZMANUALORDER AS 'zPerson-Manual Order Key',
        zPerson.ZQUESTIONTYPE AS 'zPerson-Question Type',
        zPerson.ZSUGGESTEDFORCLIENTTYPE AS 'zPerson-Suggested For Client Type',
        zPerson.ZMERGETARGETPERSON AS 'zPerson-Merge Target Person',
        CASE zPerson.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Person Not Synced with Cloud-0'
            WHEN 1 THEN 'Person Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDLOCALSTATE
        END AS 'zPerson-Cloud Local State',
        CASE zFaceCrop.ZCLOUDLOCALSTATE
            WHEN 0 THEN 'Not Synced with Cloud-0'
            WHEN 1 THEN 'Synced with Cloud-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDLOCALSTATE || ''
        END AS 'zFaceCrop-Cloud Local State',
        CASE zFaceCrop.ZCLOUDTYPE
            WHEN 0 THEN 'Has Name-0'
            WHEN 5 THEN 'Has Face Key-5'
            WHEN 12 THEN '12-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDTYPE || ''
        END AS 'zFaceCrop-Cloud Type',
        CASE zPerson.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zPerson.ZCLOUDDELETESTATE || ''
        END AS 'zPerson-Cloud Delete State',
        CASE zFaceCrop.ZCLOUDDELETESTATE
            WHEN 0 THEN 'Cloud Not Deleted-0'
            WHEN 1 THEN 'Cloud Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zFaceCrop.ZCLOUDDELETESTATE || ''
        END AS 'zFaceCrop-Cloud Delete State',
        zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',       
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
            LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSETFORFACE
            LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSONFORFACE
            LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
            LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
            LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
        WHERE zAsset.ZFACEAREAPOINTS > 0  
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                personcontactmatchingdictionary = ''
                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                facecropresourcedata_blob = ''

                # zPerson.ZCONTACTMATCHINGDICTIONARY-PLIST
                if row[67] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_zPerson-ContactMatchingDict_' + str(counter) + '.plist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[67])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            personcontactmatchingdictionary = deserialized_plist

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[11])
                            else:
                                logfunc('Error reading exported plist from zPerson-Contact Matching Dictionary' + row[11])

                # zFaceCrop.ZRESOURCEDATA-BLOB_JPG
                if row[90] is not None:
                    pathto = os.path.join(report_folder, 'Ph15-2_FaceCropFor_' + row[86] + '.jpg')
                    with open(pathto, 'wb') as file:
                        file.write(row[90])
                    facecropresourcedata_blob = media_to_html(pathto, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65], row[66],
                                  personcontactmatchingdictionary,
                                  row[68], row[69], row[70], row[71], row[72],
                                  row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                  row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89],
                                  facecropresourcedata_blob,
                                  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
                                  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
                                  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
                                  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
                                  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
                                  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
                                  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
                                  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
                                  row[156], row[157], row[158], row[159], row[160], row[161]))

                counter += 1

            description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite for' \
                          ' basic asset, people and detected faces data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 17.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph15.2-People & Faces Asset Data-SyndPL', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-Time Zone Offset-5',
                            'zAddAssetAttr-EXIF-String-6',
                            'zAsset-Modification Date-7',
                            'zAsset-Last Shared Date-8',
                            'zAddAssetAttr-Last Viewed Date-9',
                            'zAsset-Directory-Path-10',
                            'zAsset-Filename-11',
                            'zAddAssetAttr- Original Filename-12',
                            'zCldMast- Original Filename-13',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                            'zAsset- Conversation= zGenAlbum_zPK-15',
                            'zAsset-Syndication State-16',
                            'zAsset-Trashed Date-17',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-18',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-19',
                            'zAsset-Saved Asset Type-20',
                            'zAddAssetAttr-Imported by Bundle ID-21',
                            'zAddAssetAttr-Imported By Display Name-22',
                            'zAddAssetAttr-Imported by-23',
                            'zCldMast-Imported by Bundle ID-24',
                            'zCldMast-Imported by Display Name-25',
                            'zCldMast-Imported By-26',
                            'zAsset-Visibility State-27',
                            'zExtAttr-Camera Make-28',
                            'zExtAttr-Camera Model-29',
                            'zExtAttr-Lens Model-30',
                            'zAsset-Derived Camera Capture Device-31',
                            'zAddAssetAttr-Camera Captured Device-32',
                            'zAddAssetAttr-Share Type-33',
                            'zCldMast-Cloud Local State-34',
                            'zCldMast-Import Date-35',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-36',
                            'zAddAssetAttr-Import Session ID-37',
                            'zAddAssetAttr-Alt Import Image Date-38',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-39',
                            'zAsset-Cloud Batch Publish Date-40',
                            'zAsset-Cloud Server Publish Date-41',
                            'zAsset-Cloud Download Requests-42',
                            'zAsset-Cloud Batch ID-43',
                            'zAsset-Latitude-44',
                            'zExtAttr-Latitude-45',
                            'zAsset-Longitude-46',
                            'zExtAttr-Longitude-47',
                            'zAddAssetAttr-GPS Horizontal Accuracy-48',
                            'zAddAssetAttr-Location Hash-49',
                            'zAddAssetAttr-Shifted Location Valid-50',
                            'zAddAssetAttr-Shifted Location Data-51',
                            'zAddAssetAttr-Reverse Location Is Valid-52',
                            'zAddAssetAttr-Reverse Location Data-53',
                            'AAAzCldMastMedData-zOPT-54',
                            'zAddAssetAttr-Media Metadata Type-55',
                            'AAAzCldMastMedData-Data-56',
                            'CldMasterzCldMastMedData-zOPT-57',
                            'zCldMast-Media Metadata Type-58',
                            'CMzCldMastMedData-Data-59',
                            'zAsset-Bundle Scope-60',
                            'zFaceCrop-Face Area Points-61',
                            'zAsset-Face Adjustment Version-62',
                            'zAddAssetAttr-Face Regions-63',
                            'zAddAssetAttr-Face Analysis Version-64',
                            'zDetFace-Asset Visible-65',
                            'zDetFacePrint-Data-66',
                            'zPerson-Contact_Matching_Dictionary-Plist-67',
                            'zPerson-Face Count-68',
                            'zDetFace-Face Crop-69',
                            'zDetFace-Face Algorithm Version-70',
                            'zDetFace-Adjustment Version-71',
                            'zDetFace-UUID-72',
                            'zPerson-Person UUID-73',
                            'zPerson - MD ID-74',
                            'zPerson - Asset Sort Order-75',
                            'zDetFace-Confirmed Face Crop Generation State-76',
                            'zDetFace-Manual-77',
                            'zDetFace-Detection Type-78',
                            'zPerson-Detection Type-79',
                            'zDetFace-VIP Model Type-80',
                            'zDetFace-Name Source-81',
                            'zDetFace-Cloud Name Source-82',
                            'zPerson-Merge Candidate Confidence-83',
                            'zPerson-Person URI-84',
                            'zPerson-Display Name-85',
                            'zPerson-Full Name-86',
                            'zPerson-Cloud Verified Type-87',
                            'zFaceCrop-State-88',
                            'zFaceCrop-Type-89',
                            'zFaceCrop-Resource Data-90',
                            'zFaceCrop-UUID-91',
                            'zPerson-Type-92',
                            'zPerson-Verified Type-93',
                            'zPerson-Gender Type-94',
                            'zDetFace-Gender Type-95',
                            'zDetFace-Center X-96',
                            'zDetFace-Center Y-97',
                            'zPerson-Age Type Estimate-98',
                            'zDetFace-Age Type Estimate-99',
                            'zDetFace-Ethnicity Type-100',
                            'zDetFace-Skin Tone Type-101',
                            'zDetFace-Hair Type-102',
                            'zDetFace-Hair Color Type-103',
                            'zDetFace-Head Gear Type-104',
                            'zDetFace-Facial Hair Type-105',
                            'zDetFace-Has Face Mask-106',
                            'zDetFace-Pose Type-107',
                            'zDetFace-Face Expression Type-108',
                            'zDetFace-Has Smile-109',
                            'zDetFace-Smile Type-110',
                            'zDetFace-Lip Makeup Type-111',
                            'zDetFace-Eyes State-112',
                            'zDetFace-Is Left Eye Closed-113',
                            'zDetFace-Is Right Eye Closed-114',
                            'zDetFace-Gaze Center X-115',
                            'zDetFace-Gaze Center Y-116',
                            'zDetFace-Face Gaze Type-117',
                            'zDetFace-Eye Glasses Type-118',
                            'zDetFace-Eye Makeup Type-119',
                            'zDetFace-Cluster Squence Number Key-120',
                            'zDetFace-Grouping ID-121',
                            'zDetFace-Master ID-122',
                            'zDetFace-Quality-123',
                            'zDetFace-Quality Measure-124',
                            'zDetFace-Source Height-125',
                            'zDetFace-Source Width-126',
                            'zDetFace-Hidden/Asset Hidden-127',
                            'zDetFace-In Trash/Recently Deleted-128',
                            'zDetFace-Cloud Local State-129',
                            'zDetFace-Training Type-130',
                            'zDetFace.Pose Yaw-131',
                            'zDetFace-Body Center X-132',
                            'zDetFace-Body Center Y-133',
                            'zDetFace-Body Height-134',
                            'zDetFace-Body Width-135',
                            'zDetFace-Roll-136',
                            'zDetFace-Size-137',
                            'zDetFace-Cluster Squence Number-138',
                            'zDetFace-Blur Score-139',
                            'zDetFacePrint-Face Print Version-140',
                            'zMedAnlyAstAttr-Face Count-141',
                            'zDetFaceGroup-UUID-142',
                            'zDetFaceGroup-Person Builder State-143',
                            'zDetFaceGroup-UnNamed Face Count-144',
                            'zPerson-In Person Naming Model-145',
                            'zPerson-Key Face Pick Source Key-146',
                            'zPerson-Manual Order Key-147',
                            'zPerson-Question Type-148',
                            'zPerson-Suggested For Client Type-149',
                            'zPerson-Merge Target Person-150',
                            'zPerson-Cloud Local State-151',
                            'zFaceCrop-Cloud Local State-152',
                            'zFaceCrop-Cloud Type-153',
                            'zPerson-Cloud Delete State-154',
                            'zFaceCrop-Cloud Delete State-155',
                            'zFaceCrop-Invalid Merge Canidate Person UUID-156',
                            'zAsset-Active Library Scope Participation State-157',
                            'zAsset-zPK-158',
                            'zAddAssetAttr-zPK-159',
                            'zAsset-UUID = store.cloudphotodb-160',
                            'zAddAssetAttr-Master Fingerprint-161')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph15.2-People & Faces Asset Data-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph15.2-People & Faces Asset Data-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite people faces and basic asset data data')

        db.close()
        return


__artifacts_v2__ = {
    'Ph15-1-People & Faces Asset Data-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 15.1 Asset Basic People and Faces Data',
        'description': 'Parses basic asset record data from PhotoData-Photos.sqlite for basic asset people and faces data.'
                       ' The results may contain multiple records per ZASSET table Z_PK value and supports iOS 14-17.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-05-17',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-People_Faces_Data',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph15assetpeopledetfacephdapsql'
    },
    'Ph15-2-People & Faces Asset Data-SyndPL': {
        'name': 'SyndPL Photos.sqlite 15.2 Asset Basic People and Faces Data',
        'description': 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite'
                       ' for basic asset people and faces data. The results may contain multiple records'
                       ' per ZASSET table Z_PK value and supports iOS 14-17.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-05-17',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-Syndication_PL_Artifacts',
        'notes': '',
        'paths': '*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',
        'function': 'get_ph15assetpeopledetfacesyndpl'
    }
}
