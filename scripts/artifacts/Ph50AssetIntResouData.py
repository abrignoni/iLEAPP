# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses iOS 14-17 asset records from PhotoData/Photos.sqlite ZINTERNALRESOURCE and other tables.
#   This and other related parsers should provide data for investigative analysis of assets being stored locally
#   on the device verses assets being stored in iCloud Photos as the result of optimization.
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


def get_ph50intresouoptimzdataphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) < version.parse("14"):
		logfunc("Unsupported version for PhotoData/Photos.sqlite ZINTERNALRESOURCE table data from iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability-4QueryStart',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability-4QueryStart',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type-4QueryStart',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID-4QueryStart',
		CASE zAsset.ZCOMPLETE
			WHEN 1 THEN '1-Yes-1'
		END AS 'zAsset Complete',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
		CASE zAsset.ZCLOUDISMYASSET
			WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
			WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
		END AS 'zAsset-Cloud is My Asset',
		CASE zAsset.ZCLOUDISDELETABLE
			WHEN 0 THEN '0-No-0'
			WHEN 1 THEN '1-Yes-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
		END AS 'zAsset-Cloud is deletable/Asset',
		CASE zAsset.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
			WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
		END AS 'zAsset-Cloud_Local_State',
		CASE zAsset.ZVISIBILITYSTATE
			WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
			WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
		END AS 'zAsset-Visibility State',
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
		CASE zExtAttr.ZFLASHFIRED
			WHEN 0 THEN '0-No Flash-0'
			WHEN 1 THEN '1-Flash Fired-1'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
		END AS 'zExtAttr-Flash Fired',
		zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
		CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
		END AS 'zAddAssetAttr-Camera Captured Device',
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
		zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
		DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
		DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
		CASE zCldMast.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-Not Synced with Cloud-0'
			WHEN 1 THEN '1-Pending Upload-1'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Synced with Cloud-3'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
		END AS 'zCldMast-Cloud Local State',
		DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
		DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
		DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
		DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
		DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
		zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
		zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
		zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',
		CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
			WHEN 0 THEN '0-Shifted Location Not Valid-0'
			WHEN 1 THEN '1-Shifted Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
		END AS 'zAddAssetAttr-Shifted Location Valid',
		CASE AAAzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Cloud-1'
			WHEN 2 THEN '2-StillTesting-This Device-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
		END AS 'AAAzCldMastMedData-zOPT',
		zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		CASE zAsset.ZORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAsset-Orientation',
		CASE zAddAssetAttr.ZORIGINALORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAddAssetAttr-Original Orientation',
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Paorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 3 THEN '3-Screenshot-3'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
		END AS 'zAddAssetAttr-Cloud Kind Sub Type',
		CASE zAsset.ZPLAYBACKSTYLE
			WHEN 1 THEN '1-Image-1'
			WHEN 2 THEN '2-Image-Animated-2'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 4 THEN '4-Video-4'
			WHEN 5 THEN '5-Video-Looping-5'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
		END AS 'zAsset-Playback Style',
		CASE zAsset.ZPLAYBACKVARIATION
			WHEN 0 THEN '0-No_Playback_Variation-0'
			WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
			WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
		END AS 'zAsset-Playback Variation',
		zAsset.ZDURATION AS 'zAsset-Video Duration',
		zExtAttr.ZDURATION AS 'zExtAttr-Duration',
		zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
		zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
		zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
		zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
		zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
		CASE zIntResou.ZDATASTORECLASSID
			WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
			WHEN 3 THEN '3-SWY_Syndication_Asset-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
		END AS 'zIntResou-Datastore Class ID',
		CASE zAsset.ZCLOUDPLACEHOLDERKIND
			WHEN 0 THEN '0-Local&CloudMaster Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-StillTesting-2'
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
			WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
			WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
			WHEN 6 THEN '6-StillTesting-6'
			WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
			WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
			WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
		END AS 'zAsset-Cloud Placeholder Kind',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability',
		CASE zIntResou.ZLOCALAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
		END AS 'zIntResou-Local Availability Target',
		CASE zIntResou.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
			WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
			WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
			WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
		END AS 'zIntResou-Cloud Local State',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability',
		CASE zIntResou.ZREMOTEAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			WHEN 1 THEN '1-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
		END AS 'zIntResou-Remote Availability Target',
		zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
		zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
		zIntResou.ZFILEID AS 'zIntResou- File ID',
		CASE zIntResou.ZVERSION
			WHEN 0 THEN '0-IR_Asset_Standard-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
			WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
		END AS 'zIntResou-Version',
		zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type',
		CASE zIntResou.ZCLOUDSOURCETYPE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
		END AS 'zIntResou-Cloud Source Type',
		zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID',
		CASE zIntResou.ZCLOUDLASTPREFETCHDATE
			WHEN 0 THEN '0-NA-0'
			ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
		END AS 'zIntResou-Cloud Last Prefetch Date',
		zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
		DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
		zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
		zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
		zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
		CASE zCldMast.ZFULLSIZEJPEGSOURCE
			WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
			WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
		END AS 'zCldMast-Full Size JPEG Source',
		zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
		zExtAttr.ZCODEC AS 'zExtAttr-Codec',
		zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
		zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
		zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
		CASE zAsset.ZDEPTHTYPE
			WHEN 0 THEN '0-Not_Portrait-0_RT'
			ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
		END AS 'zAsset-Depth_Type',
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
		CASE zAsset.ZAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
		END AS 'zAddAssetAttr-Cloud Recovery State',
		zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
		zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
		zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
		zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
		CASE zAsset.ZFAVORITE
			WHEN 0 THEN '0-Asset Not Favorite-0'
			WHEN 1 THEN '1-Asset Favorite-1'
		END AS 'zAsset-Favorite',
		CASE zAsset.ZHIDDEN
			WHEN 0 THEN '0-Asset Not Hidden-0'
			WHEN 1 THEN '1-Asset Hidden-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
		END AS 'zAsset-Hidden',
		CASE zAsset.ZTRASHEDSTATE
			WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
		END AS 'zIntResou-Trash State',
		DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
		CASE zAsset.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
			WHEN 1 THEN '1-Cloud Asset Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
		END AS 'zAsset-Cloud Delete State',
		CASE zIntResou.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
			WHEN 1 THEN '1-Cloud IntResou Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
		END AS 'zIntResou-Cloud Delete State',
		CASE zAddAssetAttr.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP Not in Trash-0'
			WHEN 1 THEN '1-PTP In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
		END AS 'zAddAssetAttr-PTP Trashed State',
		CASE zIntResou.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
			WHEN 1 THEN '1-PTP IntResou In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
		END AS 'zIntResou-PTP Trashed State',
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
		zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
		zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
		zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
		zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
		zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
		zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
		CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
			WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
			WHEN 1 THEN '1-Asset Allowed for Analysis-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
		END AS 'zAddAssetAttr-Allowed for Analysis',
		zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
			WHEN 0 THEN '0-No Copy-0'
			WHEN 1 THEN '1-Has A Copy-1'
			WHEN 2 THEN '2-Has A Copy-2'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
		END AS 'zAddAssetAttr-Destination Asset Copy State',
		zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
		zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
		zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
		zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
		zExtAttr.ZISO AS 'zExtAttr-ISO',
		zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
		zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
		zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
		zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
		zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
		zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
		zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
		zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
		zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
		zAsset.ZHEIGHT AS 'zAsset-Height',
		zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
		zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
		zAsset.ZWIDTH AS 'zAsset-Width',
		zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
		zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
		zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
		zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
		zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
		zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
		zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
		zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
		zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
		CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
			WHEN 0 THEN '0-JPEG Original Resource-0'
			WHEN 1 THEN '1-RAW Original Resource-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
		END AS 'zAddAssetAttr-Orig Resource Choice',
		zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
		zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
		zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
		zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
		zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
		zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
		CASE zAddAssetAttr.ZSHARETYPE
			WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
			WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
		END AS 'zAddAssetAttr-Share Type',
		zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
		zAsset.Z_ENT AS 'zAsset-zENT',
		zAsset.Z_OPT AS 'zAsset-zOPT',
		zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
		zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
		zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
		zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
		zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
		zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
		zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
		zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
		zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
		zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
		zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
		zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
		zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
		zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
		zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
		zCldMast.Z_ENT AS 'zCldMast-zENT',
		zCldMast.Z_OPT AS 'zCldMast-zOPT',
		zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
		zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
		CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
		AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
		AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
		zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
		zExtAttr.Z_ENT AS 'zExtAttr-zENT',
		zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
		zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
		zIntResou.Z_PK AS 'zIntResou-zPK',
		zIntResou.Z_ENT AS 'zIntResou-zENT',
		zIntResou.Z_OPT AS 'zIntResou-zOPT',
		zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
		zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
		zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
		zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
		zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									row[228], row[229], row[230], row[231], row[232], row[233]))

				counter += 1

			description = 'Parses iOS 14 asset records from PhotoData/Photos.sqlite ZINTERNALRESOURCE and' \
						  ' other tables. This and other related parsers should provide data for investigative' \
						  ' analysis of assets being stored locally on the device verses assets being stored in' \
						  ' iCloud Photos as the result of optimization. This is very large query and script,' \
						  ' I recommend opening the TSV generated report with Zimmermans Tools' \
						  ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
						  ' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart',
							'zIntResou-Local Availability-4QueryStart',
							'zIntResou-Remote Availability-4QueryStart',
							'zIntResou-Resource Type-4QueryStart',
							'zIntResou-Datastore Sub-Type-4QueryStart',
							'zIntResou-Recipe ID-4QueryStart',
							'zAsset Complete',
							'zAsset-zPK',
							'zAddAssetAttr-zPK',
							'zAsset-UUID = store.cloudphotodb',
							'zAddAssetAttr-Master Fingerprint',
							'zIntResou-Fingerprint',
							'zAsset-Cloud is My Asset',
							'zAsset-Cloud is deletable/Asset',
							'zAsset-Cloud_Local_State',
							'zAsset-Visibility State',
							'zExtAttr-Camera Make',
							'zExtAttr-Camera Model',
							'zExtAttr-Lens Model',
							'zExtAttr-Flash Fired',
							'zExtAttr-Focal Lenght',
							'zAsset-Derived Camera Capture Device',
							'zAddAssetAttr-Camera Captured Device',
							'zAddAssetAttr-Imported by',
							'zCldMast-Imported By',
							'zAddAssetAttr-Creator Bundle ID',
							'zAddAssetAttr-Imported By Display Name',
							'zCldMast-Imported by Bundle ID',
							'zCldMast-Imported by Display Name',
							'zAsset-Saved Asset Type',
							'zAsset-Directory/Path',
							'zAsset-Filename',
							'zAddAssetAttr- Original Filename',
							'zCldMast- Original Filename',
							'zAsset-Added Date',
							'zAsset- SortToken -CameraRoll',
							'zAsset-Date Created',
							'zCldMast-Creation Date',
							'zIntResou-CldMst Date Created',
							'zAddAssetAttr-Time Zone Name',
							'zAddAssetAttr-Time Zone Offset',
							'zAddAssetAttr-Inferred Time Zone Offset',
							'zAddAssetAttr-EXIF-String',
							'zAsset-Modification Date',
							'zAsset-Last Shared Date',
							'zCldMast-Cloud Local State',
							'zCldMast-Import Date',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
							'zAddAssetAttr-Import Session ID',
							'zAddAssetAttr-Alt Import Image Date',
							'zCldMast-Import Session ID- AirDrop-StillTesting',
							'zAsset-Cloud Batch Publish Date',
							'zAsset-Cloud Server Publish Date',
							'zAsset-Cloud Download Requests',
							'zAsset-Cloud Batch ID',
							'zAddAssetAttr-Upload Attempts',
							'zAsset-Latitude',
							'zExtAttr-Latitude',
							'zAsset-Longitude',
							'zExtAttr-Longitude',
							'zAddAssetAttr-GPS Horizontal Accuracy',
							'zAddAssetAttr-Location Hash',
							'zAddAssetAttr-Reverse Location Is Valid',
							'zAddAssetAttr-Shifted Location Valid',
							'AAAzCldMastMedData-zOPT',
							'zAddAssetAttr-Media Metadata Type',
							'CldMasterzCldMastMedData-zOPT',
							'zCldMast-Media Metadata Type',
							'zAsset-Orientation',
							'zAddAssetAttr-Original Orientation',
							'zAsset-Kind',
							'zAsset-Kind-Sub-Type',
							'zAddAssetAttr-Cloud Kind Sub Type',
							'zAsset-Playback Style',
							'zAsset-Playback Variation',
							'zAsset-Video Duration',
							'zExtAttr-Duration',
							'zAsset-Video CP Duration',
							'zAddAssetAttr-Video CP Duration Time Scale',
							'zAsset-Video CP Visibility State',
							'zAddAssetAttr-Video CP Display Value',
							'zAddAssetAttr-Video CP Display Time Scale',
							'zIntResou-Datastore Class ID',
							'zAsset-Cloud Placeholder Kind',
							'zIntResou-Local Availability',
							'zIntResou-Local Availability Target',
							'zIntResou-Cloud Local State',
							'zIntResou-Remote Availability',
							'zIntResou-Remote Availability Target',
							'zIntResou-Transient Cloud Master',
							'zIntResou-Side Car Index',
							'zIntResou- File ID',
							'zIntResou-Version',
							'zAddAssetAttr- Original-File-Size',
							'zIntResou-Resource Type',
							'zIntResou-Datastore Sub-Type',
							'zIntResou-Cloud Source Type',
							'zIntResou-Data Length',
							'zIntResou-Recipe ID',
							'zIntResou-Cloud Last Prefetch Date',
							'zIntResou-Cloud Prefetch Count',
							'zIntResou- Cloud-Last-OnDemand Download-Date',
							'zAsset-Uniform Type ID',
							'zAsset-Original Color Space',
							'zCldMast-Uniform_Type_ID',
							'zCldMast-Full Size JPEG Source',
							'zAsset-HDR Gain',
							'zExtAttr-Codec',
							'zCldMast-Codec Name',
							'zCldMast-Video Frame Rate',
							'zCldMast-Placeholder State',
							'zAsset-Depth_Type',
							'zAsset-Avalanche UUID',
							'zAsset-Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud Recovery State',
							'zAddAssetAttr-Cloud State Recovery Attempts Count',
							'zAsset-Deferred Processing Needed',
							'zAddAssetAttr-Deferred Photo Identifier',
							'zAddAssetAttr-Deferred Processing Candidate Options',
							'zAsset-Has Adjustments/Camera-Effects-Filters',
							'zAsset-Adjustment Timestamp',
							'zAddAssetAttr-Editor Bundle ID',
							'zAddAssetAttr-Montage',
							'zAsset-Favorite',
							'zAsset-Hidden',
							'zAsset-Trashed State/LocalAssetRecentlyDeleted',
							'zAsset-Trashed Date',
							'zIntResou-Trash State',
							'zIntResou-Trashed Date',
							'zAsset-Cloud Delete State',
							'zIntResou-Cloud Delete State',
							'zAddAssetAttr-PTP Trashed State',
							'zIntResou-PTP Trashed State',
							'zIntResou-Cloud Delete Asset UUID With Resource Type',
							'zMedAnlyAstAttr-Media Analysis Timestamp',
							'zAsset-Analysis State Modificaion Date',
							'zAddAssetAttr- Pending View Count',
							'zAddAssetAttr- View Count',
							'zAddAssetAttr- Pending Play Count',
							'zAddAssetAttr- Play Count',
							'zAddAssetAttr- Pending Share Count',
							'zAddAssetAttr- Share Count',
							'zAddAssetAttr-Allowed for Analysis',
							'zAddAssetAttr-Scene Analysis Version',
							'zAddAssetAttr-Scene Analysis Timestamp',
							'zAddAssetAttr-Destination Asset Copy State',
							'zAddAssetAttr-Variation Suggestions States',
							'zAsset-High Frame Rate State',
							'zAsset-Video Key Frame Time Scale',
							'zAsset-Video Key Frame Value',
							'zExtAttr-ISO',
							'zExtAttr-Metering Mode',
							'zExtAttr-Sample Rate',
							'zExtAttr-Track Format',
							'zExtAttr-White Balance',
							'zExtAttr-Aperture',
							'zExtAttr-BitRate',
							'zExtAttr-Exposure Bias',
							'zExtAttr-Frames Per Second',
							'zExtAttr-Shutter Speed',
							'zAsset-Height',
							'zAddAssetAttr-Original Height',
							'zIntResou-Unoriented Height',
							'zAsset-Width',
							'zAddAssetAttr-Original Width',
							'zIntResou-Unoriented Width',
							'zAsset-Thumbnail Index',
							'zAddAssetAttr-Embedded Thumbnail Height',
							'zAddAssetAttr-Embedded Thumbnail Length',
							'zAddAssetAttr-Embedded Thumbnail Offset',
							'zAddAssetAttr-Embedded Thumbnail Width',
							'zAsset-Packed Acceptable Crop Rect',
							'zAsset-Packed Badge Attributes',
							'zAsset-Packed Preferred Crop Rect',
							'zAsset-Curation Score',
							'zAsset-Camera Processing Adjustment State',
							'zAsset-Depth Type',
							'zAddAssetAttr-Orig Resource Choice',
							'zAddAssetAttr-Spatial Over Capture Group ID',
							'zAddAssetAttr-Place Annotation Data',
							'zAddAssetAttr-Edited IPTC Attributes',
							'zAddAssetAttr-Title/Comments via Cloud Website',
							'zAddAssetAttr-Accessibility Description',
							'zAddAssetAttr-Photo Stream Tag ID',
							'zAddAssetAttr-Share Type',
							'zAsset-Overall Aesthetic Score',
							'zAsset-zENT',
							'zAsset-zOPT',
							'zAsset-Master= zCldMast-zPK',
							'zAsset-Extended Attributes= zExtAttr-zPK',
							'zAsset-Import Session Key',
							'zAsset-FOK-Cloud Feed Asset Entry Key',
							'zAsset-Computed Attributes Asset Key',
							'zAsset-Promotion Score',
							'zAsset-Media Analysis Attributes Key',
							'zAsset-Media Group UUID',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
							'zAsset.Cloud Collection GUID',
							'zAddAssetAttr-zENT',
							'ZAddAssetAttr-zOPT',
							'zAddAssetAttr-zAsset= zAsset_zPK',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
							'zAddAssetAttr-Public Global UUID',
							'zAddAssetAttr-Original Assets UUID',
							'zAddAssetAttr-Originating Asset Identifier',
							'zAddAssetAttr.Adjusted Fingerprint',
							'zCldMast-zPK= zAsset-Master',
							'zCldMast-zENT',
							'zCldMast-zOPT',
							'zCldMast-Moment Share Key= zShare-zPK',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
							'zCldMast-Originating Asset ID',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
							'CMzCldMastMedData-zENT',
							'CMzCldMastMedData-CldMast= zCldMast-zPK',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
							'AAAzCldMastMedData-zENT',
							'AAAzCldMastMedData-CldMast key',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
							'zExtAttr-zPK= zAsset-zExtendedAttributes',
							'zExtAttr-zENT',
							'zExtAttr-zOPT',
							'zExtAttr-Asset Key',
							'zIntResou-zPK',
							'zIntResou-zENT',
							'zIntResou-zOPT',
							'zIntResou-Asset= zAsset_zPK',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
							'zMedAnlyAstAttr-zEnt',
							'zMedAnlyAstAttr-zOpt',
							'zMedAnlyAstAttr-Asset= zAsset-zPK')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 14 PhotoData/Photos.sqlite')

		db.close()
		return

	elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability-4QueryStart',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability-4QueryStart',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type-4QueryStart',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID-4QueryStart',
		CASE zAsset.ZCOMPLETE
			WHEN 1 THEN '1-Yes-1'
		END AS 'zAsset Complete',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
		CASE zAsset.ZBUNDLESCOPE
			WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
			WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
			WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
			WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
		END AS 'zAsset-Bundle Scope',
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
		CASE zAsset.ZCLOUDISMYASSET
			WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
			WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
		END AS 'zAsset-Cloud is My Asset',
		CASE zAsset.ZCLOUDISDELETABLE
			WHEN 0 THEN '0-No-0'
			WHEN 1 THEN '1-Yes-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
		END AS 'zAsset-Cloud is deletable/Asset',
		CASE zAsset.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
			WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
		END AS 'zAsset-Cloud_Local_State',
		CASE zAsset.ZVISIBILITYSTATE
			WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
			WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
		END AS 'zAsset-Visibility State',
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
		CASE zExtAttr.ZFLASHFIRED
			WHEN 0 THEN '0-No Flash-0'
			WHEN 1 THEN '1-Flash Fired-1'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
		END AS 'zExtAttr-Flash Fired',
		zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
		zExtAttr.ZFOCALLENGTHIN35MM AS 'zExtAttr-Focal Lenth in 35MM',
		zExtAttr.ZDIGITALZOOMRATIO AS 'zExtAttr-Digital Zoom Ratio',
		CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
		END AS 'zAddAssetAttr-Camera Captured Device',
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
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
		DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
		DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
		CASE zCldMast.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-Not Synced with Cloud-0'
			WHEN 1 THEN '1-Pending Upload-1'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Synced with Cloud-3'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
		END AS 'zCldMast-Cloud Local State',
		DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
		DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
		DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
		DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
		DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
		zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
		zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
		zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',
		CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
			WHEN 0 THEN '0-Shifted Location Not Valid-0'
			WHEN 1 THEN '1-Shifted Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
		END AS 'zAddAssetAttr-Shifted Location Valid',
		CASE AAAzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Cloud-1'
			WHEN 2 THEN '2-StillTesting-This Device-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
		END AS 'AAAzCldMastMedData-zOPT',
		zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zAddAssetAttr.ZSYNDICATIONHISTORY AS 'zAddAssetAttr-Syndication History',
		zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVERSION AS 'zMedAnlyAstAttr-Syndication Processing Version',
		CASE zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-STILLTESTING_Wide-Camera_JPG-1'
			WHEN 2 THEN '2-STILLTESTING_Telephoto_Camear_Lens-2'
			WHEN 4 THEN '4-STILLTESTING_SWY_Asset_OrigAssetImport_SystemPackageApp-4'
			WHEN 16 THEN '16-STILLTESTING-16'
			WHEN 1024 THEN '1024-STILLTESTING_SWY_Asset_OrigAssetImport_NativeCamera-1024'
			WHEN 2048 THEN '2048-STILLTESTING-2048'
			WHEN 4096 THEN '4096-STILLTESTING_SWY_Asset_Manually_Saved-4096'
			ELSE 'Unknown-New-Value!: ' || zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE || ''
		END AS 'zMedAnlyAstAttr-Syndication Processing Value',
		CASE zAsset.ZORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAsset-Orientation',
		CASE zAddAssetAttr.ZORIGINALORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAddAssetAttr-Original Orientation',
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Paorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 3 THEN '3-Screenshot-3'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
		END AS 'zAddAssetAttr-Cloud Kind Sub Type',
		CASE zAsset.ZPLAYBACKSTYLE
			WHEN 1 THEN '1-Image-1'
			WHEN 2 THEN '2-Image-Animated-2'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 4 THEN '4-Video-4'
			WHEN 5 THEN '5-Video-Looping-5'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
		END AS 'zAsset-Playback Style',
		CASE zAsset.ZPLAYBACKVARIATION
			WHEN 0 THEN '0-No_Playback_Variation-0'
			WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
			WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
		END AS 'zAsset-Playback Variation',
		zAsset.ZDURATION AS 'zAsset-Video Duration',
		zExtAttr.ZDURATION AS 'zExtAttr-Duration',
		zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
		zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
		zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
		zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
		zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
		CASE zIntResou.ZDATASTORECLASSID
			WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
			WHEN 3 THEN '3-SWY_Syndication_Asset-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
		END AS 'zIntResou-Datastore Class ID',
		CASE zAsset.ZCLOUDPLACEHOLDERKIND
			WHEN 0 THEN '0-Local&CloudMaster Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-StillTesting-2'
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
			WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
			WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
			WHEN 6 THEN '6-StillTesting-6'
			WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
			WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
			WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
		END AS 'zAsset-Cloud Placeholder Kind',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability',
		CASE zIntResou.ZLOCALAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
		END AS 'zIntResou-Local Availability Target',
		CASE zIntResou.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
			WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
			WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
			WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
		END AS 'zIntResou-Cloud Local State',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability',
		CASE zIntResou.ZREMOTEAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			WHEN 1 THEN '1-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
		END AS 'zIntResou-Remote Availability Target',
		zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
		zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
		zIntResou.ZFILEID AS 'zIntResou- File ID',
		CASE zIntResou.ZVERSION
			WHEN 0 THEN '0-IR_Asset_Standard-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
			WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
		END AS 'zIntResou-Version',
		zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type',
		CASE zIntResou.ZCLOUDSOURCETYPE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
		END AS 'zIntResou-Cloud Source Type',
		zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID',
		CASE zIntResou.ZCLOUDLASTPREFETCHDATE
			WHEN 0 THEN '0-NA-0'
			ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
		END AS 'zIntResou-Cloud Last Prefetch Date',
		zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
		DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
		CASE zIntResou.ZUTICONFORMANCEHINT
			WHEN 0 THEN '0-NA/Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG/THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG/HEIC/quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj/Mutation_Data-37'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCOMPACTUTI || ''
		END AS 'zIntResou-Compact-UTI',
		zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
		zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
		zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
		CASE zCldMast.ZFULLSIZEJPEGSOURCE
			WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
			WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
		END AS 'zCldMast-Full Size JPEG Source',
		zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
		CASE zAsset.ZHDRTYPE
			WHEN 0 THEN '0-No-HDR-0'
			WHEN 3 THEN '3-HDR_Photo-3_RT'
			WHEN 4 THEN '4-Non-HDR_Version-4_RT'
			WHEN 5 THEN '5-HEVC_Movie-5'
			WHEN 6 THEN '6-Panorama-6_RT'
			WHEN 10 THEN '10-HDR-Gain-10'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHDRTYPE || ''
		END AS 'zAsset-zHDR_Type',
		zExtAttr.ZCODEC AS 'zExtAttr-Codec',
		zIntResou.ZCODECFOURCHARCODENAME AS 'zIntResou-Codec Four Char Code Name',
		zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
		zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
		zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
		CASE zAsset.ZDEPTHTYPE
			WHEN 0 THEN '0-Not_Portrait-0_RT'
			ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
		END AS 'zAsset-Depth_Type',
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
		CASE zAsset.ZAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
		END AS 'zAddAssetAttr-Cloud Recovery State',
		zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
		zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
		zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
		zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
		zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
		CASE zAsset.ZFAVORITE
			WHEN 0 THEN '0-Asset Not Favorite-0'
			WHEN 1 THEN '1-Asset Favorite-1'
		END AS 'zAsset-Favorite',
		CASE zAsset.ZHIDDEN
			WHEN 0 THEN '0-Asset Not Hidden-0'
			WHEN 1 THEN '1-Asset Hidden-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
		END AS 'zAsset-Hidden',
		CASE zAsset.ZTRASHEDSTATE
			WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
		END AS 'zIntResou-Trash State',
		DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
		CASE zAsset.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
			WHEN 1 THEN '1-Cloud Asset Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
		END AS 'zAsset-Cloud Delete State',
		CASE zIntResou.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
			WHEN 1 THEN '1-Cloud IntResou Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
		END AS 'zIntResou-Cloud Delete State',
		CASE zAddAssetAttr.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP Not in Trash-0'
			WHEN 1 THEN '1-PTP In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
		END AS 'zAddAssetAttr-PTP Trashed State',
		CASE zIntResou.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
			WHEN 1 THEN '1-PTP IntResou In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
		END AS 'zIntResou-PTP Trashed State',
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
		zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
		zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
		zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
		zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
		zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
		zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
		CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
			WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
			WHEN 1 THEN '1-Asset Allowed for Analysis-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
		END AS 'zAddAssetAttr-Allowed for Analysis',
		zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
		CASE zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW
			WHEN 0 THEN '0-No-0'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW || ''
		END AS 'zAddAssetAttr-Scene Analysis is From Preview',
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
			WHEN 0 THEN '0-No Copy-0'
			WHEN 1 THEN '1-Has A Copy-1'
			WHEN 2 THEN '2-Has A Copy-2'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
		END AS 'zAddAssetAttr-Destination Asset Copy State',
		zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONSCOPEIDENTIFIER AS 'zAddAssetAttr-Source Asset for Duplication Scope ID',
		zCldMast.ZSOURCEMASTERFORDUPLICATIONSCOPEIDENTIFIER AS 'zCldMast-Source Master For Duplication Scope ID',
		zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONIDENTIFIER AS 'zAddAssetAttr-Source Asset For Duplication ID',
		zCldMast.ZSOURCEMASTERFORDUPLICATIONIDENTIFIER AS 'zCldMast-Source Master for Duplication ID',
		zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
		zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
		zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
		zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
		zExtAttr.ZISO AS 'zExtAttr-ISO',
		zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
		zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
		zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
		zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
		zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
		zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
		zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
		zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
		zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
		zExtAttr.ZSLUSHSCENEBIAS AS 'zExtAttr-Slush Scene Bias',
		zExtAttr.ZSLUSHVERSION AS 'zExtAttr-Slush Version',
		zExtAttr.ZSLUSHPRESET AS 'zExtAttr-Slush Preset',
		zExtAttr.ZSLUSHWARMTHBIAS AS 'zExtAttr-Slush Warm Bias',
		zAsset.ZHEIGHT AS 'zAsset-Height',
		zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
		zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
		zAsset.ZWIDTH AS 'zAsset-Width',
		zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
		zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
		zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
		zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
		zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
		zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
		zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
		zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
		zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
		zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',		
		CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
			WHEN 0 THEN '0-JPEG Original Resource-0'
			WHEN 1 THEN '1-RAW Original Resource-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
		END AS 'zAddAssetAttr-Orig Resource Choice',
		zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
		zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
		zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
		zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
		zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
		zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
		CASE zAddAssetAttr.ZSHARETYPE
			WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
			WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
		END AS 'zAddAssetAttr-Share Type',
		zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
		zAsset.Z_ENT AS 'zAsset-zENT',
		zAsset.Z_OPT AS 'zAsset-zOPT',
		zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
		zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
		zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
		zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
		zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
		zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
		zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
		zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
		zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
		zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
		zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
		zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
		zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
		zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
		zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
		zCldMast.Z_ENT AS 'zCldMast-zENT',
		zCldMast.Z_OPT AS 'zCldMast-zOPT',
		zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
		zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
		CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
		AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
		AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
		zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
		zExtAttr.Z_ENT AS 'zExtAttr-zENT',
		zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
		zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
		zIntResou.Z_PK AS 'zIntResou-zPK',
		zIntResou.Z_ENT AS 'zIntResou-zENT',
		zIntResou.Z_OPT AS 'zIntResou-zOPT',
		zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
		zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
		zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
		zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
		zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									row[228], row[229], row[230], row[231], row[232], row[233], row[234], row[235],
									row[236], row[237], row[238], row[239], row[240], row[241], row[242], row[243],
									row[244], row[245], row[246], row[247], row[248], row[249], row[250], row[251],
									row[252], row[253], row[254], row[255], row[256], row[257]))

				counter += 1

			description = 'Parses iOS 15 asset records from PhotoData/Photos.sqlite ZINTERNALRESOURCE and' \
						  ' other tables. This and other related parsers should provide data for investigative' \
						  ' analysis of assets being stored locally on the device verses assets being stored in' \
						  ' iCloud Photos as the result of optimization. This is very large query and script,' \
						  ' I recommend opening the TSV generated report with Zimmermans Tools' \
						  ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
						  ' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart',
							'zIntResou-Local Availability-4QueryStart',
							'zIntResou-Remote Availability-4QueryStart',
							'zIntResou-Resource Type-4QueryStart',
							'zIntResou-Datastore Sub-Type-4QueryStart',
							'zIntResou-Recipe ID-4QueryStart',
							'zAsset Complete',
							'zAsset-zPK',
							'zAddAssetAttr-zPK',
							'zAsset-UUID = store.cloudphotodb',
							'zAddAssetAttr-Master Fingerprint',
							'zIntResou-Fingerprint',
							'zAsset-Bundle Scope',
							'zAsset-Syndication State',
							'zAsset-Cloud is My Asset',
							'zAsset-Cloud is deletable/Asset',
							'zAsset-Cloud_Local_State',
							'zAsset-Visibility State',
							'zExtAttr-Camera Make',
							'zExtAttr-Camera Model',
							'zExtAttr-Lens Model',
							'zExtAttr-Flash Fired',
							'zExtAttr-Focal Lenght',
							'zExtAttr-Focal Lenth in 35MM',
							'zExtAttr-Digital Zoom Ratio',
							'zAsset-Derived Camera Capture Device',
							'zAddAssetAttr-Camera Captured Device',
							'zAddAssetAttr-Imported by',
							'zCldMast-Imported By',
							'zAddAssetAttr.Imported by Bundle Identifier',
							'zAddAssetAttr-Imported By Display Name',
							'zCldMast-Imported by Bundle ID',
							'zCldMast-Imported by Display Name',
							'zAsset-Saved Asset Type',
							'zAsset-Directory/Path',
							'zAsset-Filename',
							'zAddAssetAttr- Original Filename',
							'zCldMast- Original Filename',
							'zAddAssetAttr- Syndication Identifier-SWY-Files',
							'zAsset-Added Date',
							'zAsset- SortToken -CameraRoll',
							'zAddAssetAttr-Date Created Source',
							'zAsset-Date Created',
							'zCldMast-Creation Date',
							'zIntResou-CldMst Date Created',
							'zAddAssetAttr-Time Zone Name',
							'zAddAssetAttr-Time Zone Offset',
							'zAddAssetAttr-Inferred Time Zone Offset',
							'zAddAssetAttr-EXIF-String',
							'zAsset-Modification Date',
							'zAsset-Last Shared Date',
							'zCldMast-Cloud Local State',
							'zCldMast-Import Date',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
							'zAddAssetAttr-Import Session ID',
							'zAddAssetAttr-Alt Import Image Date',
							'zCldMast-Import Session ID- AirDrop-StillTesting',
							'zAsset-Cloud Batch Publish Date',
							'zAsset-Cloud Server Publish Date',
							'zAsset-Cloud Download Requests',
							'zAsset-Cloud Batch ID',
							'zAddAssetAttr-Upload Attempts',
							'zAsset-Latitude',
							'zExtAttr-Latitude',
							'zAsset-Longitude',
							'zExtAttr-Longitude',
							'zAddAssetAttr-GPS Horizontal Accuracy',
							'zAddAssetAttr-Location Hash',
							'zAddAssetAttr-Reverse Location Is Valid',
							'zAddAssetAttr-Shifted Location Valid',
							'AAAzCldMastMedData-zOPT',
							'zAddAssetAttr-Media Metadata Type',
							'CldMasterzCldMastMedData-zOPT',
							'zCldMast-Media Metadata Type',
							'zAddAssetAttr-Syndication History',
							'zMedAnlyAstAttr-Syndication Processing Version',
							'zMedAnlyAstAttr-Syndication Processing Value',
							'zAsset-Orientation',
							'zAddAssetAttr-Original Orientation',
							'zAsset-Kind',
							'zAsset-Kind-Sub-Type',
							'zAddAssetAttr-Cloud Kind Sub Type',
							'zAsset-Playback Style',
							'zAsset-Playback Variation',
							'zAsset-Video Duration',
							'zExtAttr-Duration',
							'zAsset-Video CP Duration',
							'zAddAssetAttr-Video CP Duration Time Scale',
							'zAsset-Video CP Visibility State',
							'zAddAssetAttr-Video CP Display Value',
							'zAddAssetAttr-Video CP Display Time Scale',
							'zIntResou-Datastore Class ID',
							'zAsset-Cloud Placeholder Kind',
							'zIntResou-Local Availability',
							'zIntResou-Local Availability Target',
							'zIntResou-Cloud Local State',
							'zIntResou-Remote Availability',
							'zIntResou-Remote Availability Target',
							'zIntResou-Transient Cloud Master',
							'zIntResou-Side Car Index',
							'zIntResou- File ID',
							'zIntResou-Version',
							'zAddAssetAttr- Original-File-Size',
							'zIntResou-Resource Type',
							'zIntResou-Datastore Sub-Type',
							'zIntResou-Cloud Source Type',
							'zIntResou-Data Length',
							'zIntResou-Recipe ID',
							'zIntResou-Cloud Last Prefetch Date',
							'zIntResou-Cloud Prefetch Count',
							'zIntResou- Cloud-Last-OnDemand Download-Date',
							'zIntResou-UniformTypeID_UTI_Conformance_Hint',
							'zIntResou-Compact-UTI',
							'zAsset-Uniform Type ID',
							'zAsset-Original Color Space',
							'zCldMast-Uniform_Type_ID',
							'zCldMast-Full Size JPEG Source',
							'zAsset-HDR Gain',
							'zAsset-zHDR_Type',
							'zExtAttr-Codec',
							'zIntResou-Codec Four Char Code Name',
							'zCldMast-Codec Name',
							'zCldMast-Video Frame Rate',
							'zCldMast-Placeholder State',
							'zAsset-Depth_Type',
							'zAsset-Avalanche UUID',
							'zAsset-Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud Recovery State',
							'zAddAssetAttr-Cloud State Recovery Attempts Count',
							'zAsset-Deferred Processing Needed',
							'zAsset-Video Deferred Processing Needed',
							'zAddAssetAttr-Deferred Photo Identifier',
							'zAddAssetAttr-Deferred Processing Candidate Options',
							'zAsset-Has Adjustments/Camera-Effects-Filters',
							'zAsset-Adjustment Timestamp',
							'zAddAssetAttr-Editor Bundle ID',
							'zAddAssetAttr-Montage',
							'zAsset-Favorite',
							'zAsset-Hidden',
							'zAsset-Trashed State/LocalAssetRecentlyDeleted',
							'zAsset-Trashed Date',
							'zIntResou-Trash State',
							'zIntResou-Trashed Date',
							'zAsset-Cloud Delete State',
							'zIntResou-Cloud Delete State',
							'zAddAssetAttr-PTP Trashed State',
							'zIntResou-PTP Trashed State',
							'zIntResou-Cloud Delete Asset UUID With Resource Type',
							'zMedAnlyAstAttr-Media Analysis Timestamp',
							'zAsset-Analysis State Modificaion Date',
							'zAddAssetAttr- Pending View Count',
							'zAddAssetAttr- View Count',
							'zAddAssetAttr- Pending Play Count',
							'zAddAssetAttr- Play Count',
							'zAddAssetAttr- Pending Share Count',
							'zAddAssetAttr- Share Count',
							'zAddAssetAttr-Allowed for Analysis',
							'zAddAssetAttr-Scene Analysis Version',
							'zAddAssetAttr-Scene Analysis is From Preview',
							'zAddAssetAttr-Scene Analysis Timestamp',
							'zAddAssetAttr-Destination Asset Copy State',
							'zAddAssetAttr-Source Asset for Duplication Scope ID',
							'zCldMast-Source Master For Duplication Scope ID',
							'zAddAssetAttr-Source Asset For Duplication ID',
							'zCldMast-Source Master for Duplication ID',
							'zAddAssetAttr-Variation Suggestions States',
							'zAsset-High Frame Rate State',
							'zAsset-Video Key Frame Time Scale',
							'zAsset-Video Key Frame Value',
							'zExtAttr-ISO',
							'zExtAttr-Metering Mode',
							'zExtAttr-Sample Rate',
							'zExtAttr-Track Format',
							'zExtAttr-White Balance',
							'zExtAttr-Aperture',
							'zExtAttr-BitRate',
							'zExtAttr-Exposure Bias',
							'zExtAttr-Frames Per Second',
							'zExtAttr-Shutter Speed',
							'zExtAttr-Slush Scene Bias',
							'zExtAttr-Slush Version',
							'zExtAttr-Slush Preset',
							'zExtAttr-Slush Warm Bias',
							'zAsset-Height',
							'zAddAssetAttr-Original Height',
							'zIntResou-Unoriented Height',
							'zAsset-Width',
							'zAddAssetAttr-Original Width',
							'zIntResou-Unoriented Width',
							'zAsset-Thumbnail Index',
							'zAddAssetAttr-Embedded Thumbnail Height',
							'zAddAssetAttr-Embedded Thumbnail Length',
							'zAddAssetAttr-Embedded Thumbnail Offset',
							'zAddAssetAttr-Embedded Thumbnail Width',
							'zAsset-Packed Acceptable Crop Rect',
							'zAsset-Packed Badge Attributes',
							'zAsset-Packed Preferred Crop Rect',
							'zAsset-Curation Score',
							'zAsset-Camera Processing Adjustment State',
							'zAsset-Depth Type',
							'zAsset-Is Magic Carpet-QuicktimeMOVfile',
							'zAddAssetAttr-Orig Resource Choice',
							'zAddAssetAttr-Spatial Over Capture Group ID',
							'zAddAssetAttr-Place Annotation Data',
							'zAddAssetAttr-Edited IPTC Attributes',
							'zAddAssetAttr-Title/Comments via Cloud Website',
							'zAddAssetAttr-Accessibility Description',
							'zAddAssetAttr-Photo Stream Tag ID',
							'zAddAssetAttr-Share Type',
							'zAsset-Overall Aesthetic Score',
							'zAsset-zENT',
							'zAsset-zOPT',
							'zAsset-Master= zCldMast-zPK',
							'zAsset-Extended Attributes= zExtAttr-zPK',
							'zAsset-Import Session Key',
							'zAsset-FOK-Cloud Feed Asset Entry Key',
							'zAsset-Computed Attributes Asset Key',
							'zAsset-Promotion Score',
							'zAsset-Media Analysis Attributes Key',
							'zAsset-Media Group UUID',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
							'zAsset.Cloud Collection GUID',
							'zAddAssetAttr-zENT',
							'ZAddAssetAttr-zOPT',
							'zAddAssetAttr-zAsset= zAsset_zPK',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
							'zAddAssetAttr-Public Global UUID',
							'zAddAssetAttr-Original Assets UUID',
							'zAddAssetAttr-Originating Asset Identifier',
							'zAddAssetAttr.Adjusted Fingerprint',
							'zCldMast-zPK= zAsset-Master',
							'zCldMast-zENT',
							'zCldMast-zOPT',
							'zCldMast-Moment Share Key= zShare-zPK',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
							'zCldMast-Originating Asset ID',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
							'CMzCldMastMedData-zENT',
							'CMzCldMastMedData-CldMast= zCldMast-zPK',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
							'AAAzCldMastMedData-zENT',
							'AAAzCldMastMedData-CldMast key',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
							'zExtAttr-zPK= zAsset-zExtendedAttributes',
							'zExtAttr-zENT',
							'zExtAttr-zOPT',
							'zExtAttr-Asset Key',
							'zIntResou-zPK',
							'zIntResou-zENT',
							'zIntResou-zOPT',
							'zIntResou-Asset= zAsset_zPK',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
							'zMedAnlyAstAttr-zEnt',
							'zMedAnlyAstAttr-zOpt',
							'zMedAnlyAstAttr-Asset= zAsset-zPK')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 15 PhotoData/Photos.sqlite')

		db.close()
		return

	elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability-4QueryStart',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability-4QueryStart',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type-4QueryStart',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID-4QueryStart',
		CASE zAsset.ZCOMPLETE
			WHEN 1 THEN '1-Yes-1'
		END AS 'zAsset Complete',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
		CASE zAsset.ZBUNDLESCOPE
			WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
			WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
			WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
			WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
		END AS 'zAsset-Bundle Scope',
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
		CASE zAsset.ZCLOUDISMYASSET
			WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
			WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
		END AS 'zAsset-Cloud is My Asset',
		CASE zAsset.ZCLOUDISDELETABLE
			WHEN 0 THEN '0-No-0'
			WHEN 1 THEN '1-Yes-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
		END AS 'zAsset-Cloud is deletable/Asset',
		CASE zAsset.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
			WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
		END AS 'zAsset-Cloud_Local_State',
		CASE zAsset.ZVISIBILITYSTATE
			WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
			WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
		END AS 'zAsset-Visibility State',
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
		CASE zExtAttr.ZFLASHFIRED
			WHEN 0 THEN '0-No Flash-0'
			WHEN 1 THEN '1-Flash Fired-1'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
		END AS 'zExtAttr-Flash Fired',
		zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
		zExtAttr.ZFOCALLENGTHIN35MM AS 'zExtAttr-Focal Lenth in 35MM',
		zExtAttr.ZDIGITALZOOMRATIO AS 'zExtAttr-Digital Zoom Ratio',
		CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
		END AS 'zAddAssetAttr-Camera Captured Device',
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
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
		CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
			WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
			WHEN 1 THEN '1-Asset-In-Active-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
		END AS 'zAsset-Active Library Scope Participation State',
		CASE zAsset.ZLIBRARYSCOPESHARESTATE
			WHEN 0 THEN '0-Asset-Not-In-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
		END AS 'zAsset-Library Scope Share State- StillTesting',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
		DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
		DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
		DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
		CASE zCldMast.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-Not Synced with Cloud-0'
			WHEN 1 THEN '1-Pending Upload-1'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Synced with Cloud-3'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
		END AS 'zCldMast-Cloud Local State',
		DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
		DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
		DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
		DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
		DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
		zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
		zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
		zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',
		CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
			WHEN 0 THEN '0-Shifted Location Not Valid-0'
			WHEN 1 THEN '1-Shifted Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
		END AS 'zAddAssetAttr-Shifted Location Valid',
		CASE AAAzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Cloud-1'
			WHEN 2 THEN '2-StillTesting-This Device-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
		END AS 'AAAzCldMastMedData-zOPT',
		zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		CASE zAsset.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'zAsset-Search Index Rebuild State',
		zAddAssetAttr.ZSYNDICATIONHISTORY AS 'zAddAssetAttr-Syndication History',
		zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVERSION AS 'zMedAnlyAstAttr-Syndication Processing Version',
		CASE zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-STILLTESTING_Wide-Camera_JPG-1'
			WHEN 2 THEN '2-STILLTESTING_Telephoto_Camear_Lens-2'
			WHEN 4 THEN '4-STILLTESTING_SWY_Asset_OrigAssetImport_SystemPackageApp-4'
			WHEN 16 THEN '16-STILLTESTING-16'
			WHEN 1024 THEN '1024-STILLTESTING_SWY_Asset_OrigAssetImport_NativeCamera-1024'
			WHEN 2048 THEN '2048-STILLTESTING-2048'
			WHEN 4096 THEN '4096-STILLTESTING_SWY_Asset_Manually_Saved-4096'
			ELSE 'Unknown-New-Value!: ' || zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE || ''
		END AS 'zMedAnlyAstAttr-Syndication Processing Value',
		CASE zAsset.ZORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAsset-Orientation',
		CASE zAddAssetAttr.ZORIGINALORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAddAssetAttr-Original Orientation',
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Paorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 3 THEN '3-Screenshot-3'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
		END AS 'zAddAssetAttr-Cloud Kind Sub Type',
		CASE zAsset.ZPLAYBACKSTYLE
			WHEN 1 THEN '1-Image-1'
			WHEN 2 THEN '2-Image-Animated-2'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 4 THEN '4-Video-4'
			WHEN 5 THEN '5-Video-Looping-5'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
		END AS 'zAsset-Playback Style',
		CASE zAsset.ZPLAYBACKVARIATION
			WHEN 0 THEN '0-No_Playback_Variation-0'
			WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
			WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
		END AS 'zAsset-Playback Variation',
		zAsset.ZDURATION AS 'zAsset-Video Duration',
		zExtAttr.ZDURATION AS 'zExtAttr-Duration',
		zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
		zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
		zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
		zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
		zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
		CASE zIntResou.ZDATASTORECLASSID
			WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
			WHEN 3 THEN '3-SWY_Syndication_Asset-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
		END AS 'zIntResou-Datastore Class ID',
		CASE zAsset.ZCLOUDPLACEHOLDERKIND
			WHEN 0 THEN '0-Local&CloudMaster Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-StillTesting-2'
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
			WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
			WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
			WHEN 6 THEN '6-StillTesting-6'
			WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
			WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
			WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
		END AS 'zAsset-Cloud Placeholder Kind',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability',
		CASE zIntResou.ZLOCALAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
		END AS 'zIntResou-Local Availability Target',
		CASE zIntResou.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
			WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
			WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
			WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
		END AS 'zIntResou-Cloud Local State',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability',
		CASE zIntResou.ZREMOTEAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			WHEN 1 THEN '1-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
		END AS 'zIntResou-Remote Availability Target',
		zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
		zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
		zIntResou.ZFILEID AS 'zIntResou- File ID',
		CASE zIntResou.ZVERSION
			WHEN 0 THEN '0-IR_Asset_Standard-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
			WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
		END AS 'zIntResou-Version',
		zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type',
		CASE zIntResou.ZCLOUDSOURCETYPE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
		END AS 'zIntResou-Cloud Source Type',
		zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID',
		CASE zIntResou.ZCLOUDLASTPREFETCHDATE
			WHEN 0 THEN '0-NA-0'
			ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
		END AS 'zIntResou-Cloud Last Prefetch Date',
		zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
		DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
		CASE zIntResou.ZUTICONFORMANCEHINT
			WHEN 0 THEN '0-NA/Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG/THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG/HEIC/quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj/Mutation_Data-37'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCOMPACTUTI || ''
		END AS 'zIntResou-Compact-UTI',
		zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
		zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
		zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
		CASE zCldMast.ZFULLSIZEJPEGSOURCE
			WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
			WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
		END AS 'zCldMast-Full Size JPEG Source',
		zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
		CASE zAsset.ZHDRTYPE
			WHEN 0 THEN '0-No-HDR-0'
			WHEN 3 THEN '3-HDR_Photo-3_RT'
			WHEN 4 THEN '4-Non-HDR_Version-4_RT'
			WHEN 5 THEN '5-HEVC_Movie-5'
			WHEN 6 THEN '6-Panorama-6_RT'
			WHEN 10 THEN '10-HDR-Gain-10'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHDRTYPE || ''
		END AS 'zAsset-zHDR_Type',
		zExtAttr.ZCODEC AS 'zExtAttr-Codec',
		zIntResou.ZCODECFOURCHARCODENAME AS 'zIntResou-Codec Four Char Code Name',
		zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
		zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
		zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
		CASE zAsset.ZDEPTHTYPE
			WHEN 0 THEN '0-Not_Portrait-0_RT'
			ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
		END AS 'zAsset-Depth_Type',
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
		CASE zAsset.ZAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
		END AS 'zAddAssetAttr-Cloud Recovery State',
		zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
		zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
		zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
		zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
		zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
		CASE zAsset.ZFAVORITE
			WHEN 0 THEN '0-Asset Not Favorite-0'
			WHEN 1 THEN '1-Asset Favorite-1'
		END AS 'zAsset-Favorite',
		CASE zAsset.ZHIDDEN
			WHEN 0 THEN '0-Asset Not Hidden-0'
			WHEN 1 THEN '1-Asset Hidden-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
		END AS 'zAsset-Hidden',
		CASE zAsset.ZTRASHEDSTATE
			WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		CASE zAsset.ZDELETEREASON
			WHEN 1 THEN '1-StillTesting Delete-Reason-1'
			WHEN 2 THEN '2-StillTesting Delete-Reason-2'
			WHEN 3 THEN '3-StillTesting Delete-Reason-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
		END AS 'zAsset-Delete-Reason',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
		END AS 'zIntResou-Trash State',
		DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
		CASE zAsset.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
			WHEN 1 THEN '1-Cloud Asset Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
		END AS 'zAsset-Cloud Delete State',
		CASE zIntResou.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
			WHEN 1 THEN '1-Cloud IntResou Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
		END AS 'zIntResou-Cloud Delete State',
		CASE zAddAssetAttr.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP Not in Trash-0'
			WHEN 1 THEN '1-PTP In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
		END AS 'zAddAssetAttr-PTP Trashed State',
		CASE zIntResou.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
			WHEN 1 THEN '1-PTP IntResou In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
		END AS 'zIntResou-PTP Trashed State',
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
		zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
		zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
		zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
		zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
		zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
		zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
		CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
			WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
			WHEN 1 THEN '1-Asset Allowed for Analysis-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
		END AS 'zAddAssetAttr-Allowed for Analysis',
		zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
		CASE zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW
			WHEN 0 THEN '0-No-0'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW || ''
		END AS 'zAddAssetAttr-Scene Analysis is From Preview',
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		CASE zAsset.ZDUPLICATEASSETVISIBILITYSTATE
			WHEN 0 THEN '0-No-Duplicates-0'
			WHEN 1 THEN '1-Has Duplicate-1'
			WHEN 2 THEN '2-Is a Duplicate-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDUPLICATEASSETVISIBILITYSTATE || ''
		END AS 'zAsset-Duplication Asset Visibility State',
		CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
			WHEN 0 THEN '0-No Copy-0'
			WHEN 1 THEN '1-Has A Copy-1'
			WHEN 2 THEN '2-Has A Copy-2'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
		END AS 'zAddAssetAttr-Destination Asset Copy State',
		CASE zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE
			WHEN 0 THEN '0-Unknown-StillTesting-0'
			WHEN 1 THEN '1-Unknown-StillTesting-1'
			WHEN 2 THEN '2-Unknown-StillTesting-2'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE || ''
		END AS 'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
		zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONSCOPEIDENTIFIER AS 'zAddAssetAttr-Source Asset for Duplication Scope ID',
		zCldMast.ZSOURCEMASTERFORDUPLICATIONSCOPEIDENTIFIER AS 'zCldMast-Source Master For Duplication Scope ID',
		zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONIDENTIFIER AS 'zAddAssetAttr-Source Asset For Duplication ID',
		zCldMast.ZSOURCEMASTERFORDUPLICATIONIDENTIFIER AS 'zCldMast-Source Master for Duplication ID',
		zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
		zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
		zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
		zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
		zExtAttr.ZISO AS 'zExtAttr-ISO',
		zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
		zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
		zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
		zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
		zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
		zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
		zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
		zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
		zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
		zExtAttr.ZSLUSHSCENEBIAS AS 'zExtAttr-Slush Scene Bias',
		zExtAttr.ZSLUSHVERSION AS 'zExtAttr-Slush Version',
		zExtAttr.ZSLUSHPRESET AS 'zExtAttr-Slush Preset',
		zExtAttr.ZSLUSHWARMTHBIAS AS 'zExtAttr-Slush Warm Bias',
		zAsset.ZHEIGHT AS 'zAsset-Height',
		zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
		zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
		zAsset.ZWIDTH AS 'zAsset-Width',
		zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
		zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
		zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
		zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
		zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
		zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
		zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
		zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
		zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
		zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',		
		CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
			WHEN 0 THEN '0-JPEG Original Resource-0'
			WHEN 1 THEN '1-RAW Original Resource-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
		END AS 'zAddAssetAttr-Orig Resource Choice',
		zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
		zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
		zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
		zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
		zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
		zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
		CASE zAddAssetAttr.ZSHARETYPE
			WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
			WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
		END AS 'zAddAssetAttr-Share Type',
		zAddAssetAttr.ZLIBRARYSCOPEASSETCONTRIBUTORSTOUPDATE AS 'zAddAssetAttr-Library Scope Asset Contributors To Update',
		zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
		zAsset.Z_ENT AS 'zAsset-zENT',
		zAsset.Z_OPT AS 'zAsset-zOPT',
		zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
		zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
		zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
		zAsset.ZPHOTOANALYSISATTRIBUTES AS 'zAsset-Photo Analysis Attributes Key',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
		zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
		zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
		zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
		zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
		zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
		zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
		zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
		zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
		zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
		zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
		zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
		zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
		zCldMast.Z_ENT AS 'zCldMast-zENT',
		zCldMast.Z_OPT AS 'zCldMast-zOPT',
		zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
		zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
		CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
		AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
		AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
		zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
		zExtAttr.Z_ENT AS 'zExtAttr-zENT',
		zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
		zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
		zIntResou.Z_PK AS 'zIntResou-zPK',
		zIntResou.Z_ENT AS 'zIntResou-zENT',
		zIntResou.Z_OPT AS 'zIntResou-zOPT',
		zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
		zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
		zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
		zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
		zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									row[228], row[229], row[230], row[231], row[232], row[233], row[234], row[235],
									row[236], row[237], row[238], row[239], row[240], row[241], row[242], row[243],
									row[244], row[245], row[246], row[247], row[248], row[249], row[250], row[251],
									row[252], row[253], row[254], row[255], row[256], row[257], row[258], row[259],
									row[260], row[261], row[262], row[263], row[264], row[265], row[266], row[267]))

				counter += 1

			description = 'Parses iOS 16 asset records from PhotoData/Photos.sqlite ZINTERNALRESOURCE and' \
						' other tables. This and other related parsers should provide data for investigative' \
						' analysis of assets being stored locally on the device verses assets being stored in' \
						' iCloud Photos as the result of optimization. This is very large query and script,' \
						' I recommend opening the TSV generated report with Zimmermans Tools' \
						' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
						' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart',
							'zIntResou-Local Availability-4QueryStart',
							'zIntResou-Remote Availability-4QueryStart',
							'zIntResou-Resource Type-4QueryStart',
							'zIntResou-Datastore Sub-Type-4QueryStart',
							'zIntResou-Recipe ID-4QueryStart',
							'zAsset Complete',
							'zAsset-zPK',
							'zAddAssetAttr-zPK',
							'zAsset-UUID = store.cloudphotodb',
							'zAddAssetAttr-Master Fingerprint',
							'zIntResou-Fingerprint',
							'zAsset-Bundle Scope',
							'zAsset-Syndication State',
							'zAsset-Cloud is My Asset',
							'zAsset-Cloud is deletable/Asset',
							'zAsset-Cloud_Local_State',
							'zAsset-Visibility State',
							'zExtAttr-Camera Make',
							'zExtAttr-Camera Model',
							'zExtAttr-Lens Model',
							'zExtAttr-Flash Fired',
							'zExtAttr-Focal Lenght',
							'zExtAttr-Focal Lenth in 35MM',
							'zExtAttr-Digital Zoom Ratio',
							'zAsset-Derived Camera Capture Device',
							'zAddAssetAttr-Camera Captured Device',
							'zAddAssetAttr-Imported by',
							'zCldMast-Imported By',
							'zAddAssetAttr.Imported by Bundle Identifier',
							'zAddAssetAttr-Imported By Display Name',
							'zCldMast-Imported by Bundle ID',
							'zCldMast-Imported by Display Name',
							'zAsset-Saved Asset Type',
							'zAsset-Directory/Path',
							'zAsset-Filename',
							'zAddAssetAttr- Original Filename',
							'zCldMast- Original Filename',
							'zAddAssetAttr- Syndication Identifier-SWY-Files',
							'zAsset-Active Library Scope Participation State',
							'zAsset-Library Scope Share State- StillTesting',
							'zAsset-Added Date',
							'zAsset- SortToken -CameraRoll',
							'zAddAssetAttr-Date Created Source',
							'zAsset-Date Created',
							'zCldMast-Creation Date',
							'zIntResou-CldMst Date Created',
							'zAddAssetAttr-Time Zone Name',
							'zAddAssetAttr-Time Zone Offset',
							'zAddAssetAttr-Inferred Time Zone Offset',
							'zAddAssetAttr-EXIF-String',
							'zAsset-Modification Date',
							'zAddAssetAttr-Last Viewed Date',
							'zAsset-Last Shared Date',
							'zCldMast-Cloud Local State',
							'zCldMast-Import Date',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
							'zAddAssetAttr-Import Session ID',
							'zAddAssetAttr-Alt Import Image Date',
							'zCldMast-Import Session ID- AirDrop-StillTesting',
							'zAsset-Cloud Batch Publish Date',
							'zAsset-Cloud Server Publish Date',
							'zAsset-Cloud Download Requests',
							'zAsset-Cloud Batch ID',
							'zAddAssetAttr-Upload Attempts',
							'zAsset-Latitude',
							'zExtAttr-Latitude',
							'zAsset-Longitude',
							'zExtAttr-Longitude',
							'zAddAssetAttr-GPS Horizontal Accuracy',
							'zAddAssetAttr-Location Hash',
							'zAddAssetAttr-Reverse Location Is Valid',
							'zAddAssetAttr-Shifted Location Valid',
							'AAAzCldMastMedData-zOPT',
							'zAddAssetAttr-Media Metadata Type',
							'CldMasterzCldMastMedData-zOPT',
							'zCldMast-Media Metadata Type',
							'zAsset-Search Index Rebuild State',
							'zAddAssetAttr-Syndication History',
							'zMedAnlyAstAttr-Syndication Processing Version',
							'zMedAnlyAstAttr-Syndication Processing Value',
							'zAsset-Orientation',
							'zAddAssetAttr-Original Orientation',
							'zAsset-Kind',
							'zAsset-Kind-Sub-Type',
							'zAddAssetAttr-Cloud Kind Sub Type',
							'zAsset-Playback Style',
							'zAsset-Playback Variation',
							'zAsset-Video Duration',
							'zExtAttr-Duration',
							'zAsset-Video CP Duration',
							'zAddAssetAttr-Video CP Duration Time Scale',
							'zAsset-Video CP Visibility State',
							'zAddAssetAttr-Video CP Display Value',
							'zAddAssetAttr-Video CP Display Time Scale',
							'zIntResou-Datastore Class ID',
							'zAsset-Cloud Placeholder Kind',
							'zIntResou-Local Availability',
							'zIntResou-Local Availability Target',
							'zIntResou-Cloud Local State',
							'zIntResou-Remote Availability',
							'zIntResou-Remote Availability Target',
							'zIntResou-Transient Cloud Master',
							'zIntResou-Side Car Index',
							'zIntResou- File ID',
							'zIntResou-Version',
							'zAddAssetAttr- Original-File-Size',
							'zIntResou-Resource Type',
							'zIntResou-Datastore Sub-Type',
							'zIntResou-Cloud Source Type',
							'zIntResou-Data Length',
							'zIntResou-Recipe ID',
							'zIntResou-Cloud Last Prefetch Date',
							'zIntResou-Cloud Prefetch Count',
							'zIntResou- Cloud-Last-OnDemand Download-Date',
							'zIntResou-UniformTypeID_UTI_Conformance_Hint',
							'zIntResou-Compact-UTI',
							'zAsset-Uniform Type ID',
							'zAsset-Original Color Space',
							'zCldMast-Uniform_Type_ID',
							'zCldMast-Full Size JPEG Source',
							'zAsset-HDR Gain',
							'zAsset-zHDR_Type',
							'zExtAttr-Codec',
							'zIntResou-Codec Four Char Code Name',
							'zCldMast-Codec Name',
							'zCldMast-Video Frame Rate',
							'zCldMast-Placeholder State',
							'zAsset-Depth_Type',
							'zAsset-Avalanche UUID',
							'zAsset-Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud Recovery State',
							'zAddAssetAttr-Cloud State Recovery Attempts Count',
							'zAsset-Deferred Processing Needed',
							'zAsset-Video Deferred Processing Needed',
							'zAddAssetAttr-Deferred Photo Identifier',
							'zAddAssetAttr-Deferred Processing Candidate Options',
							'zAsset-Has Adjustments/Camera-Effects-Filters',
							'zAsset-Adjustment Timestamp',
							'zAddAssetAttr-Editor Bundle ID',
							'zAddAssetAttr-Montage',
							'zAsset-Favorite',
							'zAsset-Hidden',
							'zAsset-Trashed State/LocalAssetRecentlyDeleted',
							'zAsset-Trashed Date',
							'zAsset-Trashed by Participant= zSharePartic_zPK',
							'zAsset-Delete-Reason',
							'zIntResou-Trash State',
							'zIntResou-Trashed Date',
							'zAsset-Cloud Delete State',
							'zIntResou-Cloud Delete State',
							'zAddAssetAttr-PTP Trashed State',
							'zIntResou-PTP Trashed State',
							'zIntResou-Cloud Delete Asset UUID With Resource Type',
							'zMedAnlyAstAttr-Media Analysis Timestamp',
							'zAsset-Analysis State Modificaion Date',
							'zAddAssetAttr- Pending View Count',
							'zAddAssetAttr- View Count',
							'zAddAssetAttr- Pending Play Count',
							'zAddAssetAttr- Play Count',
							'zAddAssetAttr- Pending Share Count',
							'zAddAssetAttr- Share Count',
							'zAddAssetAttr-Allowed for Analysis',
							'zAddAssetAttr-Scene Analysis Version',
							'zAddAssetAttr-Scene Analysis is From Preview',
							'zAddAssetAttr-Scene Analysis Timestamp',
							'zAsset-Duplication Asset Visibility State',
							'zAddAssetAttr-Destination Asset Copy State',
							'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
							'zAddAssetAttr-Source Asset for Duplication Scope ID',
							'zCldMast-Source Master For Duplication Scope ID',
							'zAddAssetAttr-Source Asset For Duplication ID',
							'zCldMast-Source Master for Duplication ID',
							'zAddAssetAttr-Variation Suggestions States',
							'zAsset-High Frame Rate State',
							'zAsset-Video Key Frame Time Scale',
							'zAsset-Video Key Frame Value',
							'zExtAttr-ISO',
							'zExtAttr-Metering Mode',
							'zExtAttr-Sample Rate',
							'zExtAttr-Track Format',
							'zExtAttr-White Balance',
							'zExtAttr-Aperture',
							'zExtAttr-BitRate',
							'zExtAttr-Exposure Bias',
							'zExtAttr-Frames Per Second',
							'zExtAttr-Shutter Speed',
							'zExtAttr-Slush Scene Bias',
							'zExtAttr-Slush Version',
							'zExtAttr-Slush Preset',
							'zExtAttr-Slush Warm Bias',
							'zAsset-Height',
							'zAddAssetAttr-Original Height',
							'zIntResou-Unoriented Height',
							'zAsset-Width',
							'zAddAssetAttr-Original Width',
							'zIntResou-Unoriented Width',
							'zAsset-Thumbnail Index',
							'zAddAssetAttr-Embedded Thumbnail Height',
							'zAddAssetAttr-Embedded Thumbnail Length',
							'zAddAssetAttr-Embedded Thumbnail Offset',
							'zAddAssetAttr-Embedded Thumbnail Width',
							'zAsset-Packed Acceptable Crop Rect',
							'zAsset-Packed Badge Attributes',
							'zAsset-Packed Preferred Crop Rect',
							'zAsset-Curation Score',
							'zAsset-Camera Processing Adjustment State',
							'zAsset-Depth Type',
							'zAsset-Is Magic Carpet-QuicktimeMOVfile',
							'zAddAssetAttr-Orig Resource Choice',
							'zAddAssetAttr-Spatial Over Capture Group ID',
							'zAddAssetAttr-Place Annotation Data',
							'zAddAssetAttr-Edited IPTC Attributes',
							'zAddAssetAttr-Title/Comments via Cloud Website',
							'zAddAssetAttr-Accessibility Description',
							'zAddAssetAttr-Photo Stream Tag ID',
							'zAddAssetAttr-Share Type',
							'zAddAssetAttr-Library Scope Asset Contributors To Update',
							'zAsset-Overall Aesthetic Score',
							'zAsset-zENT',
							'zAsset-zOPT',
							'zAsset-Master= zCldMast-zPK',
							'zAsset-Extended Attributes= zExtAttr-zPK',
							'zAsset-Import Session Key',
							'zAsset-Photo Analysis Attributes Key',
							'zAsset-FOK-Cloud Feed Asset Entry Key',
							'zAsset-Computed Attributes Asset Key',
							'zAsset-Promotion Score',
							'zAsset-Media Analysis Attributes Key',
							'zAsset-Media Group UUID',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
							'zAsset.Cloud Collection GUID',
							'zAddAssetAttr-zENT',
							'ZAddAssetAttr-zOPT',
							'zAddAssetAttr-zAsset= zAsset_zPK',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
							'zAddAssetAttr-Public Global UUID',
							'zAddAssetAttr-Original Assets UUID',
							'zAddAssetAttr-Originating Asset Identifier',
							'zAddAssetAttr.Adjusted Fingerprint',
							'zCldMast-zPK= zAsset-Master',
							'zCldMast-zENT',
							'zCldMast-zOPT',
							'zCldMast-Moment Share Key= zShare-zPK',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
							'zCldMast-Originating Asset ID',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
							'CMzCldMastMedData-zENT',
							'CMzCldMastMedData-CldMast= zCldMast-zPK',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
							'AAAzCldMastMedData-zENT',
							'AAAzCldMastMedData-CldMast key',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
							'zExtAttr-zPK= zAsset-zExtendedAttributes',
							'zExtAttr-zENT',
							'zExtAttr-zOPT',
							'zExtAttr-Asset Key',
							'zIntResou-zPK',
							'zIntResou-zENT',
							'zIntResou-zOPT',
							'zIntResou-Asset= zAsset_zPK',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
							'zMedAnlyAstAttr-zEnt',
							'zMedAnlyAstAttr-zOpt',
							'zMedAnlyAstAttr-Asset= zAsset-zPK')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 16 PhotoData/Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("17"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability-4QueryStart',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability-4QueryStart',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type-4QueryStart',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID-4QueryStart',
		CASE zAsset.ZCOMPLETE
			WHEN 1 THEN '1-Yes-1'
		END AS 'zAsset Complete',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
		CASE zAsset.ZBUNDLESCOPE
			WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
			WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
			WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
			WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
		END AS 'zAsset-Bundle Scope',
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
		CASE zAsset.ZCLOUDISMYASSET
			WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
			WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
		END AS 'zAsset-Cloud is My Asset',
		CASE zAsset.ZCLOUDISDELETABLE
			WHEN 0 THEN '0-No-0'
			WHEN 1 THEN '1-Yes-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
		END AS 'zAsset-Cloud is deletable/Asset',
		CASE zAsset.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
			WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
		END AS 'zAsset-Cloud_Local_State',
		CASE zAsset.ZVISIBILITYSTATE
			WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
			WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
		END AS 'zAsset-Visibility State',
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
		CASE zExtAttr.ZFLASHFIRED
			WHEN 0 THEN '0-No Flash-0'
			WHEN 1 THEN '1-Flash Fired-1'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
		END AS 'zExtAttr-Flash Fired',
		zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
		zExtAttr.ZFOCALLENGTHIN35MM AS 'zExtAttr-Focal Lenth in 35MM',
		zExtAttr.ZDIGITALZOOMRATIO AS 'zExtAttr-Digital Zoom Ratio',
		CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera/Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
		END AS 'zAddAssetAttr-Camera Captured Device',
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
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
		CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
			WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
			WHEN 1 THEN '1-Asset-In-Active-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
		END AS 'zAsset-Active Library Scope Participation State',
		CASE zAsset.ZLIBRARYSCOPESHARESTATE
			WHEN 0 THEN '0-Asset-Not-In-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
		END AS 'zAsset-Library Scope Share State- StillTesting',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
		DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
		DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
		DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
		CASE zCldMast.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-Not Synced with Cloud-0'
			WHEN 1 THEN '1-Pending Upload-1'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Synced with Cloud-3'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
		END AS 'zCldMast-Cloud Local State',
		DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
		DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
		DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
		DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
		DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
		zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
		zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
		zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',
		CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
			WHEN 0 THEN '0-Shifted Location Not Valid-0'
			WHEN 1 THEN '1-Shifted Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
		END AS 'zAddAssetAttr-Shifted Location Valid',
		CASE AAAzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Cloud-1'
			WHEN 2 THEN '2-StillTesting-This Device-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
		END AS 'AAAzCldMastMedData-zOPT',
		zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		CASE zAsset.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'zAsset-Search Index Rebuild State',
		zAddAssetAttr.ZSYNDICATIONHISTORY AS 'zAddAssetAttr-Syndication History',
		zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVERSION AS 'zMedAnlyAstAttr-Syndication Processing Version',
		CASE zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-STILLTESTING_Wide-Camera_JPG-1'
			WHEN 2 THEN '2-STILLTESTING_Telephoto_Camear_Lens-2'
			WHEN 4 THEN '4-STILLTESTING_SWY_Asset_OrigAssetImport_SystemPackageApp-4'
			WHEN 16 THEN '16-STILLTESTING-16'
			WHEN 1024 THEN '1024-STILLTESTING_SWY_Asset_OrigAssetImport_NativeCamera-1024'
			WHEN 2048 THEN '2048-STILLTESTING-2048'
			WHEN 4096 THEN '4096-STILLTESTING_SWY_Asset_Manually_Saved-4096'
			ELSE 'Unknown-New-Value!: ' || zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE || ''
		END AS 'zMedAnlyAstAttr-Syndication Processing Value',
		CASE zAsset.ZORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAsset-Orientation',
		CASE zAddAssetAttr.ZORIGINALORIENTATION
			WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
			WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
			WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
			WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
			WHEN 5 THEN '5-Vertical-Camera-(top)-5'
			WHEN 6 THEN '6-Vertical-Camera-(top)-6'
			WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
			WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
		END AS 'zAddAssetAttr-Original Orientation',
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Paorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 3 THEN '3-Screenshot-3'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
		END AS 'zAddAssetAttr-Cloud Kind Sub Type',
		CASE zAsset.ZPLAYBACKSTYLE
			WHEN 1 THEN '1-Image-1'
			WHEN 2 THEN '2-Image-Animated-2'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 4 THEN '4-Video-4'
			WHEN 5 THEN '5-Video-Looping-5'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
		END AS 'zAsset-Playback Style',
		CASE zAsset.ZPLAYBACKVARIATION
			WHEN 0 THEN '0-No_Playback_Variation-0'
			WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
			WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
		END AS 'zAsset-Playback Variation',
		zAsset.ZDURATION AS 'zAsset-Video Duration',
		zExtAttr.ZDURATION AS 'zExtAttr-Duration',
		zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
		zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
		zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
		zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
		zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
		CASE zIntResou.ZDATASTORECLASSID
			WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
			WHEN 3 THEN '3-SWY_Syndication_Asset-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
		END AS 'zIntResou-Datastore Class ID',
		CASE zAsset.ZCLOUDPLACEHOLDERKIND
			WHEN 0 THEN '0-Local&CloudMaster Asset-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-StillTesting-2'
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
			WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
			WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
			WHEN 6 THEN '6-StillTesting-6'
			WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
			WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
			WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
		END AS 'zAsset-Cloud Placeholder Kind',
		CASE zIntResou.ZLOCALAVAILABILITY
			WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
			WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
			WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
		END AS 'zIntResou-Local Availability',
		CASE zIntResou.ZLOCALAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
		END AS 'zIntResou-Local Availability Target',
		CASE zIntResou.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
			WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
			WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
			WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
		END AS 'zIntResou-Cloud Local State',
		CASE zIntResou.ZREMOTEAVAILABILITY
			WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
			WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
		END AS 'zIntResou-Remote Availability',
		CASE zIntResou.ZREMOTEAVAILABILITYTARGET
			WHEN 0 THEN '0-StillTesting-0'
			WHEN 1 THEN '1-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
		END AS 'zIntResou-Remote Availability Target',
		zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
		zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
		zIntResou.ZFILEID AS 'zIntResou- File ID',
		CASE zIntResou.ZVERSION
			WHEN 0 THEN '0-IR_Asset_Standard-0'
			WHEN 1 THEN '1-StillTesting-1'
			WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
			WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
		END AS 'zIntResou-Version',
		zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
		CASE zIntResou.ZRESOURCETYPE
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
			WHEN 3 THEN '3-Live-Photo-3'
			WHEN 5 THEN '5-Adjustement-Data-5'
			WHEN 6 THEN '6-Screenshot-6'
			WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
			WHEN 13 THEN '13-Movie-13'
			WHEN 14 THEN '14-Wallpaper-14'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
		END AS 'zIntResou-Resource Type',
		CASE zIntResou.ZDATASTORESUBTYPE
			WHEN 0 THEN '0-No Cloud Inter Resource-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
		END AS 'zIntResou-Datastore Sub-Type',
		CASE zIntResou.ZCLOUDSOURCETYPE
			WHEN 0 THEN '0-NA-0'
			WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
			WHEN 2 THEN '2-Photo-with-Adjustments-2'
			WHEN 3 THEN '3-JPG-Large-Thumb-3'
			WHEN 4 THEN '4-JPG-Med-Thumb-4'
			WHEN 5 THEN '5-JPG-Small-Thumb-5'
			WHEN 6 THEN '6-Video-Med-Data-6'
			WHEN 7 THEN '7-Video-Small-Data-7'
			WHEN 8 THEN '8-MP4-Cloud-Share-8'
			WHEN 9 THEN '9-StillTesting'
			WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
			WHEN 11 THEN '11-StillTesting'
			WHEN 12 THEN '12-StillTesting'
			WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
			WHEN 14 THEN '14-Wallpaper-14'
			WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
			WHEN 16 THEN '16-Video-with-Adjustments-16'
			WHEN 17 THEN '17-RAW_Photo-17_RT'
			WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
			WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
			WHEN 20 THEN '20-StillTesting'
			WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
			WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
			WHEN 23 THEN '23-StillTesting'
			WHEN 24 THEN '24-StillTesting'
			WHEN 25 THEN '25-StillTesting'
			WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
			WHEN 27 THEN '27-StillTesting'
			WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
		END AS 'zIntResou-Cloud Source Type',
		zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
		CASE zIntResou.ZRECIPEID
			WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
			WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
			WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
			WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
			WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
			WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
			WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
			WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
			WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
			WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
			WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
			WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
			WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
			WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
			WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
			WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
			WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
		END AS 'zIntResou-Recipe ID',
		CASE zIntResou.ZCLOUDLASTPREFETCHDATE
			WHEN 0 THEN '0-NA-0'
			ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
		END AS 'zIntResou-Cloud Last Prefetch Date',
		zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
		DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
		CASE zIntResou.ZUTICONFORMANCEHINT
			WHEN 0 THEN '0-NA/Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG/THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG/HEIC/quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj/Mutation_Data-37'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCOMPACTUTI || ''
		END AS 'zIntResou-Compact-UTI',
		zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
		zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
		zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
		CASE zCldMast.ZFULLSIZEJPEGSOURCE
			WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
			WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
			ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
		END AS 'zCldMast-Full Size JPEG Source',
		zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
		CASE zAsset.ZHDRTYPE
			WHEN 0 THEN '0-No-HDR-0'
			WHEN 3 THEN '3-HDR_Photo-3_RT'
			WHEN 4 THEN '4-Non-HDR_Version-4_RT'
			WHEN 5 THEN '5-HEVC_Movie-5'
			WHEN 6 THEN '6-Panorama-6_RT'
			WHEN 10 THEN '10-HDR-Gain-10'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHDRTYPE || ''
		END AS 'zAsset-zHDR_Type',
		zExtAttr.ZCODEC AS 'zExtAttr-Codec',
		zIntResou.ZCODECFOURCHARCODENAME AS 'zIntResou-Codec Four Char Code Name',
		zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
		zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
		zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
		CASE zAsset.ZDEPTHTYPE
			WHEN 0 THEN '0-Not_Portrait-0_RT'
			ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
		END AS 'zAsset-Depth_Type',
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
		CASE zAsset.ZAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
		CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
		END AS 'zAddAssetAttr-Cloud Recovery State',
		zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
		zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
		zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
		zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
		zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
		CASE zAsset.ZFAVORITE
			WHEN 0 THEN '0-Asset Not Favorite-0'
			WHEN 1 THEN '1-Asset Favorite-1'
		END AS 'zAsset-Favorite',
		CASE zAsset.ZHIDDEN
			WHEN 0 THEN '0-Asset Not Hidden-0'
			WHEN 1 THEN '1-Asset Hidden-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
		END AS 'zAsset-Hidden',
		CASE zAsset.ZTRASHEDSTATE
			WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		CASE zAsset.ZDELETEREASON
			WHEN 1 THEN '1-StillTesting Delete-Reason-1'
			WHEN 2 THEN '2-StillTesting Delete-Reason-2'
			WHEN 3 THEN '3-StillTesting Delete-Reason-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
		END AS 'zAsset-Delete-Reason',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
		END AS 'zIntResou-Trash State',
		DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
		CASE zAsset.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
			WHEN 1 THEN '1-Cloud Asset Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
		END AS 'zAsset-Cloud Delete State',
		CASE zIntResou.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
			WHEN 1 THEN '1-Cloud IntResou Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
		END AS 'zIntResou-Cloud Delete State',
		CASE zAddAssetAttr.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP Not in Trash-0'
			WHEN 1 THEN '1-PTP In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
		END AS 'zAddAssetAttr-PTP Trashed State',
		CASE zIntResou.ZPTPTRASHEDSTATE
			WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
			WHEN 1 THEN '1-PTP IntResou In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
		END AS 'zIntResou-PTP Trashed State',
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
		zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
		zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
		zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
		zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
		zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
		zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
		CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
			WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
			WHEN 1 THEN '1-Asset Allowed for Analysis-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
		END AS 'zAddAssetAttr-Allowed for Analysis',
		zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
		CASE zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW
			WHEN 0 THEN '0-No-0'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW || ''
		END AS 'zAddAssetAttr-Scene Analysis is From Preview',
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		CASE zAsset.ZDUPLICATEASSETVISIBILITYSTATE
			WHEN 0 THEN '0-No-Duplicates-0'
			WHEN 1 THEN '1-Has Duplicate-1'
			WHEN 2 THEN '2-Is a Duplicate-2'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDUPLICATEASSETVISIBILITYSTATE || ''
		END AS 'zAsset-Duplication Asset Visibility State',
		CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
			WHEN 0 THEN '0-No Copy-0'
			WHEN 1 THEN '1-Has A Copy-1'
			WHEN 2 THEN '2-Has A Copy-2'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
		END AS 'zAddAssetAttr-Destination Asset Copy State',
		CASE zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE
			WHEN 0 THEN '0-Unknown-StillTesting-0'
			WHEN 1 THEN '1-Unknown-StillTesting-1'
			WHEN 2 THEN '2-Unknown-StillTesting-2'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE || ''
		END AS 'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
		zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONSCOPEIDENTIFIER AS 'zAddAssetAttr-Source Asset for Duplication Scope ID',
		zCldMast.ZSOURCEMASTERFORDUPLICATIONSCOPEIDENTIFIER AS 'zCldMast-Source Master For Duplication Scope ID',
		zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONIDENTIFIER AS 'zAddAssetAttr-Source Asset For Duplication ID',
		zCldMast.ZSOURCEMASTERFORDUPLICATIONIDENTIFIER AS 'zCldMast-Source Master for Duplication ID',
		zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
		zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
		zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
		zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
		zExtAttr.ZISO AS 'zExtAttr-ISO',
		zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
		zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
		zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
		zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
		zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
		zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
		zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
		zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
		zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
		zExtAttr.ZSLUSHSCENEBIAS AS 'zExtAttr-Slush Scene Bias',
		zExtAttr.ZSLUSHVERSION AS 'zExtAttr-Slush Version',
		zExtAttr.ZSLUSHPRESET AS 'zExtAttr-Slush Preset',
		zExtAttr.ZSLUSHWARMTHBIAS AS 'zExtAttr-Slush Warm Bias',
		zAsset.ZHEIGHT AS 'zAsset-Height',
		zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
		zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
		zAsset.ZWIDTH AS 'zAsset-Width',
		zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
		zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
		zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
		zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
		zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
		zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
		zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
		zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
		zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
		zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
		zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',		
		CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
			WHEN 0 THEN '0-JPEG Original Resource-0'
			WHEN 1 THEN '1-RAW Original Resource-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
		END AS 'zAddAssetAttr-Orig Resource Choice',
		CASE zAsset.ZSPATIALTYPE
			WHEN 0 THEN '0-UnknownTesting-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZSPATIALTYPE || ''
		END AS 'zAsset-Spatial Type',
		zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
		zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
		zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
		zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
		zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
		zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
		CASE zAddAssetAttr.ZSHARETYPE
			WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
			WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
		END AS 'zAddAssetAttr-Share Type',
		zAddAssetAttr.ZLIBRARYSCOPEASSETCONTRIBUTORSTOUPDATE AS 'zAddAssetAttr-Library Scope Asset Contributors To Update',
		zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
		zAsset.Z_ENT AS 'zAsset-zENT',
		zAsset.Z_OPT AS 'zAsset-zOPT',
		zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
		zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
		zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
		zAsset.ZPHOTOANALYSISATTRIBUTES AS 'zAsset-Photo Analysis Attributes Key',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
		zAsset.ZICONICSCORE AS 'zAsset-Iconic Score',
		zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
		zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
		zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
		zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
		zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
		zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
		zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
		zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
		zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
		zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
		zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
		zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
		zCldMast.Z_ENT AS 'zCldMast-zENT',
		zCldMast.Z_OPT AS 'zCldMast-zOPT',
		zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
		zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
		CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
		AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
		AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
		zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
		zExtAttr.Z_ENT AS 'zExtAttr-zENT',
		zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
		zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
		zIntResou.Z_PK AS 'zIntResou-zPK',
		zIntResou.Z_ENT AS 'zIntResou-zENT',
		zIntResou.Z_OPT AS 'zIntResou-zOPT',
		zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
		zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
		zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
		zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
		zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									row[228], row[229], row[230], row[231], row[232], row[233], row[234], row[235],
									row[236], row[237], row[238], row[239], row[240], row[241], row[242], row[243],
									row[244], row[245], row[246], row[247], row[248], row[249], row[250], row[251],
									row[252], row[253], row[254], row[255], row[256], row[257], row[258], row[259],
									row[260], row[261], row[262], row[263], row[264], row[265], row[266], row[267],
									row[268], row[269]))

				counter += 1

			description = 'Parses iOS 17 asset records from PhotoData/Photos.sqlite ZINTERNALRESOURCE' \
							' and other tables. This and other related parsers should provide data for investigative' \
							' analysis of assets being stored locally on the device verses assets being stored in' \
							' iCloud Photos as the result of optimization. This is very large query and script,' \
							' I recommend opening the TSV generated report with Zimmermans Tools' \
							' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
							' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart',
							'zIntResou-Local Availability-4QueryStart',
							'zIntResou-Remote Availability-4QueryStart',
							'zIntResou-Resource Type-4QueryStart',
							'zIntResou-Datastore Sub-Type-4QueryStart',
							'zIntResou-Recipe ID-4QueryStart',
							'zAsset Complete',
							'zAsset-zPK',
							'zAddAssetAttr-zPK',
							'zAsset-UUID = store.cloudphotodb',
							'zAddAssetAttr-Master Fingerprint',
							'zIntResou-Fingerprint',
							'zAsset-Bundle Scope',
							'zAsset-Syndication State',
							'zAsset-Cloud is My Asset',
							'zAsset-Cloud is deletable/Asset',
							'zAsset-Cloud_Local_State',
							'zAsset-Visibility State',
							'zExtAttr-Camera Make',
							'zExtAttr-Camera Model',
							'zExtAttr-Lens Model',
							'zExtAttr-Flash Fired',
							'zExtAttr-Focal Lenght',
							'zExtAttr-Focal Lenth in 35MM',
							'zExtAttr-Digital Zoom Ratio',
							'zAsset-Derived Camera Capture Device',
							'zAddAssetAttr-Camera Captured Device',
							'zAddAssetAttr-Imported by',
							'zCldMast-Imported By',
							'zAddAssetAttr.Imported by Bundle Identifier',
							'zAddAssetAttr-Imported By Display Name',
							'zCldMast-Imported by Bundle ID',
							'zCldMast-Imported by Display Name',
							'zAsset-Saved Asset Type',
							'zAsset-Directory/Path',
							'zAsset-Filename',
							'zAddAssetAttr- Original Filename',
							'zCldMast- Original Filename',
							'zAddAssetAttr- Syndication Identifier-SWY-Files',
							'zAsset-Active Library Scope Participation State',
							'zAsset-Library Scope Share State- StillTesting',
							'zAsset-Added Date',
							'zAsset- SortToken -CameraRoll',
							'zAddAssetAttr-Date Created Source',
							'zAsset-Date Created',
							'zCldMast-Creation Date',
							'zIntResou-CldMst Date Created',
							'zAddAssetAttr-Time Zone Name',
							'zAddAssetAttr-Time Zone Offset',
							'zAddAssetAttr-Inferred Time Zone Offset',
							'zAddAssetAttr-EXIF-String',
							'zAsset-Modification Date',
							'zAddAssetAttr-Last Viewed Date',
							'zAsset-Last Shared Date',
							'zCldMast-Cloud Local State',
							'zCldMast-Import Date',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
							'zAddAssetAttr-Import Session ID',
							'zAddAssetAttr-Alt Import Image Date',
							'zCldMast-Import Session ID- AirDrop-StillTesting',
							'zAsset-Cloud Batch Publish Date',
							'zAsset-Cloud Server Publish Date',
							'zAsset-Cloud Download Requests',
							'zAsset-Cloud Batch ID',
							'zAddAssetAttr-Upload Attempts',
							'zAsset-Latitude',
							'zExtAttr-Latitude',
							'zAsset-Longitude',
							'zExtAttr-Longitude',
							'zAddAssetAttr-GPS Horizontal Accuracy',
							'zAddAssetAttr-Location Hash',
							'zAddAssetAttr-Reverse Location Is Valid',
							'zAddAssetAttr-Shifted Location Valid',
							'AAAzCldMastMedData-zOPT',
							'zAddAssetAttr-Media Metadata Type',
							'CldMasterzCldMastMedData-zOPT',
							'zCldMast-Media Metadata Type',
							'zAsset-Search Index Rebuild State',
							'zAddAssetAttr-Syndication History',
							'zMedAnlyAstAttr-Syndication Processing Version',
							'zMedAnlyAstAttr-Syndication Processing Value',
							'zAsset-Orientation',
							'zAddAssetAttr-Original Orientation',
							'zAsset-Kind',
							'zAsset-Kind-Sub-Type',
							'zAddAssetAttr-Cloud Kind Sub Type',
							'zAsset-Playback Style',
							'zAsset-Playback Variation',
							'zAsset-Video Duration',
							'zExtAttr-Duration',
							'zAsset-Video CP Duration',
							'zAddAssetAttr-Video CP Duration Time Scale',
							'zAsset-Video CP Visibility State',
							'zAddAssetAttr-Video CP Display Value',
							'zAddAssetAttr-Video CP Display Time Scale',
							'zIntResou-Datastore Class ID',
							'zAsset-Cloud Placeholder Kind',
							'zIntResou-Local Availability',
							'zIntResou-Local Availability Target',
							'zIntResou-Cloud Local State',
							'zIntResou-Remote Availability',
							'zIntResou-Remote Availability Target',
							'zIntResou-Transient Cloud Master',
							'zIntResou-Side Car Index',
							'zIntResou- File ID',
							'zIntResou-Version',
							'zAddAssetAttr- Original-File-Size',
							'zIntResou-Resource Type',
							'zIntResou-Datastore Sub-Type',
							'zIntResou-Cloud Source Type',
							'zIntResou-Data Length',
							'zIntResou-Recipe ID',
							'zIntResou-Cloud Last Prefetch Date',
							'zIntResou-Cloud Prefetch Count',
							'zIntResou- Cloud-Last-OnDemand Download-Date',
							'zIntResou-UniformTypeID_UTI_Conformance_Hint',
							'zIntResou-Compact-UTI',
							'zAsset-Uniform Type ID',
							'zAsset-Original Color Space',
							'zCldMast-Uniform_Type_ID',
							'zCldMast-Full Size JPEG Source',
							'zAsset-HDR Gain',
							'zAsset-zHDR_Type',
							'zExtAttr-Codec',
							'zIntResou-Codec Four Char Code Name',
							'zCldMast-Codec Name',
							'zCldMast-Video Frame Rate',
							'zCldMast-Placeholder State',
							'zAsset-Depth_Type',
							'zAsset-Avalanche UUID',
							'zAsset-Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
							'zAddAssetAttr-Cloud Recovery State',
							'zAddAssetAttr-Cloud State Recovery Attempts Count',
							'zAsset-Deferred Processing Needed',
							'zAsset-Video Deferred Processing Needed',
							'zAddAssetAttr-Deferred Photo Identifier',
							'zAddAssetAttr-Deferred Processing Candidate Options',
							'zAsset-Has Adjustments/Camera-Effects-Filters',
							'zAsset-Adjustment Timestamp',
							'zAddAssetAttr-Editor Bundle ID',
							'zAddAssetAttr-Montage',
							'zAsset-Favorite',
							'zAsset-Hidden',
							'zAsset-Trashed State/LocalAssetRecentlyDeleted',
							'zAsset-Trashed Date',
							'zAsset-Trashed by Participant= zSharePartic_zPK',
							'zAsset-Delete-Reason',
							'zIntResou-Trash State',
							'zIntResou-Trashed Date',
							'zAsset-Cloud Delete State',
							'zIntResou-Cloud Delete State',
							'zAddAssetAttr-PTP Trashed State',
							'zIntResou-PTP Trashed State',
							'zIntResou-Cloud Delete Asset UUID With Resource Type',
							'zMedAnlyAstAttr-Media Analysis Timestamp',
							'zAsset-Analysis State Modificaion Date',
							'zAddAssetAttr- Pending View Count',
							'zAddAssetAttr- View Count',
							'zAddAssetAttr- Pending Play Count',
							'zAddAssetAttr- Play Count',
							'zAddAssetAttr- Pending Share Count',
							'zAddAssetAttr- Share Count',
							'zAddAssetAttr-Allowed for Analysis',
							'zAddAssetAttr-Scene Analysis Version',
							'zAddAssetAttr-Scene Analysis is From Preview',
							'zAddAssetAttr-Scene Analysis Timestamp',
							'zAsset-Duplication Asset Visibility State',
							'zAddAssetAttr-Destination Asset Copy State',
							'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
							'zAddAssetAttr-Source Asset for Duplication Scope ID',
							'zCldMast-Source Master For Duplication Scope ID',
							'zAddAssetAttr-Source Asset For Duplication ID',
							'zCldMast-Source Master for Duplication ID',
							'zAddAssetAttr-Variation Suggestions States',
							'zAsset-High Frame Rate State',
							'zAsset-Video Key Frame Time Scale',
							'zAsset-Video Key Frame Value',
							'zExtAttr-ISO',
							'zExtAttr-Metering Mode',
							'zExtAttr-Sample Rate',
							'zExtAttr-Track Format',
							'zExtAttr-White Balance',
							'zExtAttr-Aperture',
							'zExtAttr-BitRate',
							'zExtAttr-Exposure Bias',
							'zExtAttr-Frames Per Second',
							'zExtAttr-Shutter Speed',
							'zExtAttr-Slush Scene Bias',
							'zExtAttr-Slush Version',
							'zExtAttr-Slush Preset',
							'zExtAttr-Slush Warm Bias',
							'zAsset-Height',
							'zAddAssetAttr-Original Height',
							'zIntResou-Unoriented Height',
							'zAsset-Width',
							'zAddAssetAttr-Original Width',
							'zIntResou-Unoriented Width',
							'zAsset-Thumbnail Index',
							'zAddAssetAttr-Embedded Thumbnail Height',
							'zAddAssetAttr-Embedded Thumbnail Length',
							'zAddAssetAttr-Embedded Thumbnail Offset',
							'zAddAssetAttr-Embedded Thumbnail Width',
							'zAsset-Packed Acceptable Crop Rect',
							'zAsset-Packed Badge Attributes',
							'zAsset-Packed Preferred Crop Rect',
							'zAsset-Curation Score',
							'zAsset-Camera Processing Adjustment State',
							'zAsset-Depth Type',
							'zAsset-Is Magic Carpet-QuicktimeMOVfile',
							'zAddAssetAttr-Orig Resource Choice',
							'zAsset-Spatial Type',
							'zAddAssetAttr-Spatial Over Capture Group ID',
							'zAddAssetAttr-Place Annotation Data',
							'zAddAssetAttr-Edited IPTC Attributes',
							'zAddAssetAttr-Title/Comments via Cloud Website',
							'zAddAssetAttr-Accessibility Description',
							'zAddAssetAttr-Photo Stream Tag ID',
							'zAddAssetAttr-Share Type',
							'zAddAssetAttr-Library Scope Asset Contributors To Update',
							'zAsset-Overall Aesthetic Score',
							'zAsset-zENT',
							'zAsset-zOPT',
							'zAsset-Master= zCldMast-zPK',
							'zAsset-Extended Attributes= zExtAttr-zPK',
							'zAsset-Import Session Key',
							'zAsset-Photo Analysis Attributes Key',
							'zAsset-FOK-Cloud Feed Asset Entry Key',
							'zAsset-Computed Attributes Asset Key',
							'zAsset-Promotion Score',
							'zAsset-Iconic Score',
							'zAsset-Media Analysis Attributes Key',
							'zAsset-Media Group UUID',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
							'zAsset.Cloud Collection GUID',
							'zAddAssetAttr-zENT',
							'ZAddAssetAttr-zOPT',
							'zAddAssetAttr-zAsset= zAsset_zPK',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
							'zAddAssetAttr-Public Global UUID',
							'zAddAssetAttr-Original Assets UUID',
							'zAddAssetAttr-Originating Asset Identifier',
							'zAddAssetAttr.Adjusted Fingerprint',
							'zCldMast-zPK= zAsset-Master',
							'zCldMast-zENT',
							'zCldMast-zOPT',
							'zCldMast-Moment Share Key= zShare-zPK',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
							'zCldMast-Originating Asset ID',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
							'CMzCldMastMedData-zENT',
							'CMzCldMastMedData-CldMast= zCldMast-zPK',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
							'AAAzCldMastMedData-zENT',
							'AAAzCldMastMedData-CldMast key',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
							'zExtAttr-zPK= zAsset-zExtendedAttributes',
							'zExtAttr-zENT',
							'zExtAttr-zOPT',
							'zExtAttr-Asset Key',
							'zIntResou-zPK',
							'zIntResou-zENT',
							'zIntResou-zOPT',
							'zIntResou-Asset= zAsset_zPK',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
							'zMedAnlyAstAttr-zEnt',
							'zMedAnlyAstAttr-zOpt',
							'zMedAnlyAstAttr-Asset= zAsset-zPK')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 17 PhotoData/Photos.sqlite')

		db.close()
		return

def get_ph50intresouoptimzdatasyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):

		for file_found in files_found:
			file_found = str(file_found)

			if file_found.endswith('.sqlite'):
				break

		if report_folder.endswith('/') or report_folder.endswith('\\'):
			report_folder = report_folder[:-1]
		iosversion = scripts.artifacts.artGlobals.versionf
		if version.parse(iosversion) < version.parse("14"):
			logfunc(
				"Unsupported version for SyndicationPL/Photos.sqlite ZINTERNALRESOURCE table data from iOS " + iosversion)
		if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
			file_found = str(files_found[0])
			db = open_sqlite_db_readonly(file_found)
			cursor = db.cursor()

			cursor.execute("""
			SELECT
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability-4QueryStart',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability-4QueryStart',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type-4QueryStart',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID-4QueryStart',
			CASE zAsset.ZCOMPLETE
				WHEN 1 THEN '1-Yes-1'
			END AS 'zAsset Complete',
			zAsset.Z_PK AS 'zAsset-zPK',
			zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
			zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
			zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
			zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
			CASE zAsset.ZCLOUDISMYASSET
				WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
				WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
			END AS 'zAsset-Cloud is My Asset',
			CASE zAsset.ZCLOUDISDELETABLE
				WHEN 0 THEN '0-No-0'
				WHEN 1 THEN '1-Yes-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
			END AS 'zAsset-Cloud is deletable/Asset',
			CASE zAsset.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
				WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
			END AS 'zAsset-Cloud_Local_State',
			CASE zAsset.ZVISIBILITYSTATE
				WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
				WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
			END AS 'zAsset-Visibility State',
			zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
			zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
			zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
			CASE zExtAttr.ZFLASHFIRED
				WHEN 0 THEN '0-No Flash-0'
				WHEN 1 THEN '1-Flash Fired-1'
				ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
			END AS 'zExtAttr-Flash Fired',
			zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
			CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
			END AS 'zAsset-Derived Camera Capture Device',
			CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
			END AS 'zAddAssetAttr-Camera Captured Device',
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
			zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
			zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
			zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
			zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
			zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
			zAsset.ZFILENAME AS 'zAsset-Filename',
			zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
			zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
			DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
			DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
			DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
			DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
			zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
			zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
			zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
			zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
			DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
			DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
			CASE zCldMast.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-Not Synced with Cloud-0'
				WHEN 1 THEN '1-Pending Upload-1'
				WHEN 2 THEN '2-StillTesting'
				WHEN 3 THEN '3-Synced with Cloud-3'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
			END AS 'zCldMast-Cloud Local State',
			DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
			DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
			zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
			DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
			zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
			DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
			DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
			zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
			zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
			zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
			CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
				WHEN 0 THEN '0-Reverse Location Not Valid-0'
				WHEN 1 THEN '1-Reverse Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
			END AS 'zAddAssetAttr-Reverse Location Is Valid',
			CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
				WHEN 0 THEN '0-Shifted Location Not Valid-0'
				WHEN 1 THEN '1-Shifted Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
			END AS 'zAddAssetAttr-Shifted Location Valid',
			CASE AAAzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Cloud-1'
				WHEN 2 THEN '2-StillTesting-This Device-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
			END AS 'AAAzCldMastMedData-zOPT',
			zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
			CASE CMzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
				WHEN 2 THEN '2-StillTesting-Local_Asset-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
			END AS 'CldMasterzCldMastMedData-zOPT',
			zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
			CASE zAsset.ZORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAsset-Orientation',
			CASE zAddAssetAttr.ZORIGINALORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAddAssetAttr-Original Orientation',
			CASE zAsset.ZKIND
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
			END AS 'zAsset-Kind',
			CASE zAsset.ZKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-Paorama-1'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
			END AS 'zAsset-Kind-Sub-Type',
			CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-StillTesting'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 3 THEN '3-Screenshot-3'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
			END AS 'zAddAssetAttr-Cloud Kind Sub Type',
			CASE zAsset.ZPLAYBACKSTYLE
				WHEN 1 THEN '1-Image-1'
				WHEN 2 THEN '2-Image-Animated-2'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 4 THEN '4-Video-4'
				WHEN 5 THEN '5-Video-Looping-5'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
			END AS 'zAsset-Playback Style',
			CASE zAsset.ZPLAYBACKVARIATION
				WHEN 0 THEN '0-No_Playback_Variation-0'
				WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
				WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
			END AS 'zAsset-Playback Variation',
			zAsset.ZDURATION AS 'zAsset-Video Duration',
			zExtAttr.ZDURATION AS 'zExtAttr-Duration',
			zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
			zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
			zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
			zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
			zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
			CASE zIntResou.ZDATASTORECLASSID
				WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
				WHEN 3 THEN '3-SWY_Syndication_Asset-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
			END AS 'zIntResou-Datastore Class ID',
			CASE zAsset.ZCLOUDPLACEHOLDERKIND
				WHEN 0 THEN '0-Local&CloudMaster Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-StillTesting-2'
				WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
				WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
				WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
				WHEN 6 THEN '6-StillTesting-6'
				WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
				WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
				WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
			END AS 'zAsset-Cloud Placeholder Kind',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability',
			CASE zIntResou.ZLOCALAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
			END AS 'zIntResou-Local Availability Target',
			CASE zIntResou.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
				WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
				WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
				WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
			END AS 'zIntResou-Cloud Local State',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability',
			CASE zIntResou.ZREMOTEAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				WHEN 1 THEN '1-StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
			END AS 'zIntResou-Remote Availability Target',
			zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
			zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
			zIntResou.ZFILEID AS 'zIntResou- File ID',
			CASE zIntResou.ZVERSION
				WHEN 0 THEN '0-IR_Asset_Standard-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
				WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
			END AS 'zIntResou-Version',
			zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type',
			CASE zIntResou.ZCLOUDSOURCETYPE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
			END AS 'zIntResou-Cloud Source Type',
			zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID',
			CASE zIntResou.ZCLOUDLASTPREFETCHDATE
				WHEN 0 THEN '0-NA-0'
				ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
			END AS 'zIntResou-Cloud Last Prefetch Date',
			zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
			DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
			zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
			zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
			zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
			CASE zCldMast.ZFULLSIZEJPEGSOURCE
				WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
				WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
			END AS 'zCldMast-Full Size JPEG Source',
			zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
			zExtAttr.ZCODEC AS 'zExtAttr-Codec',
			zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
			zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
			zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
			CASE zAsset.ZDEPTHTYPE
				WHEN 0 THEN '0-Not_Portrait-0_RT'
				ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
			END AS 'zAsset-Depth_Type',
			zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
			CASE zAsset.ZAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
			END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
			END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
				WHEN 0 THEN '0-StillTesting'
				WHEN 1 THEN '1-StillTesting'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
			END AS 'zAddAssetAttr-Cloud Recovery State',
			zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
			zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
			zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
			zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
			CASE zAsset.ZHASADJUSTMENTS
				WHEN 0 THEN '0-No-Adjustments-0'
				WHEN 1 THEN '1-Yes-Adjustments-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
			END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
			DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
			zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
			zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
			CASE zAsset.ZFAVORITE
				WHEN 0 THEN '0-Asset Not Favorite-0'
				WHEN 1 THEN '1-Asset Favorite-1'
			END AS 'zAsset-Favorite',
			CASE zAsset.ZHIDDEN
				WHEN 0 THEN '0-Asset Not Hidden-0'
				WHEN 1 THEN '1-Asset Hidden-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
			END AS 'zAsset-Hidden',
			CASE zAsset.ZTRASHEDSTATE
				WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
			END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
			DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
			CASE zIntResou.ZTRASHEDSTATE
				WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
			END AS 'zIntResou-Trash State',
			DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
			CASE zAsset.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
				WHEN 1 THEN '1-Cloud Asset Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
			END AS 'zAsset-Cloud Delete State',
			CASE zIntResou.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
				WHEN 1 THEN '1-Cloud IntResou Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
			END AS 'zIntResou-Cloud Delete State',
			CASE zAddAssetAttr.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP Not in Trash-0'
				WHEN 1 THEN '1-PTP In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
			END AS 'zAddAssetAttr-PTP Trashed State',
			CASE zIntResou.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
				WHEN 1 THEN '1-PTP IntResou In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
			END AS 'zIntResou-PTP Trashed State',
			zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
			DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
			DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
			zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
			zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
			zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
			zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
			zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
			zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
			CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
				WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
				WHEN 1 THEN '1-Asset Allowed for Analysis-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
			END AS 'zAddAssetAttr-Allowed for Analysis',
			zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
			DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
			CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
				WHEN 0 THEN '0-No Copy-0'
				WHEN 1 THEN '1-Has A Copy-1'
				WHEN 2 THEN '2-Has A Copy-2'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
			END AS 'zAddAssetAttr-Destination Asset Copy State',
			zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
			zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
			zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
			zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
			zExtAttr.ZISO AS 'zExtAttr-ISO',
			zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
			zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
			zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
			zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
			zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
			zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
			zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
			zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
			zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
			zAsset.ZHEIGHT AS 'zAsset-Height',
			zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
			zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
			zAsset.ZWIDTH AS 'zAsset-Width',
			zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
			zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
			zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
			zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
			zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
			zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
			zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
			zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
			zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
			CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
				WHEN 0 THEN '0-JPEG Original Resource-0'
				WHEN 1 THEN '1-RAW Original Resource-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
			END AS 'zAddAssetAttr-Orig Resource Choice',
			zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
			zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
			zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
			zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
			zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
			zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
			zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
			CASE zAddAssetAttr.ZSHARETYPE
				WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
				WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
			END AS 'zAddAssetAttr-Share Type',
			zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
			zAsset.Z_ENT AS 'zAsset-zENT',
			zAsset.Z_OPT AS 'zAsset-zOPT',
			zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
			zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
			zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
			zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
			zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
			zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
			zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
			zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
			zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
			zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
			zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
			zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
			zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
			zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
			zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
			zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
			zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
			zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
			zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
			zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
			zCldMast.Z_ENT AS 'zCldMast-zENT',
			zCldMast.Z_OPT AS 'zCldMast-zOPT',
			zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
			zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
			zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
			zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
			CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
			CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
			CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
			AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
			AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
			AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
			AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
			zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
			zExtAttr.Z_ENT AS 'zExtAttr-zENT',
			zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
			zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
			zIntResou.Z_PK AS 'zIntResou-zPK',
			zIntResou.Z_ENT AS 'zIntResou-zENT',
			zIntResou.Z_OPT AS 'zIntResou-zOPT',
			zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
			zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
			zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
			zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
			zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
			FROM ZASSET zAsset
				LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
				LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
				LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
				LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
				LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
				LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									  row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									  row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									  row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									  row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									  row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									  row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									  row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									  row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									  row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									  row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									  row[228], row[229], row[230], row[231], row[232], row[233]))

					counter += 1

				description = 'Parses iOS 14 asset records from Syndication.photos.library/database/Photos.sqlite ZINTERNALRESOURCE and' \
							  ' other tables. This and other related parsers should provide data for investigative' \
							  ' analysis of assets being stored locally on the device verses assets being stored in' \
							  ' iCloud Photos as the result of optimization. This is very large query and script,' \
							  ' I recommend opening the TSV generated report with Zimmermans Tools' \
							  ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
							  ' and filter the results.'
				report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
				report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
				report.add_script()
				data_headers = ('zAsset-Date Created-4QueryStart',
								'zIntResou-Local Availability-4QueryStart',
								'zIntResou-Remote Availability-4QueryStart',
								'zIntResou-Resource Type-4QueryStart',
								'zIntResou-Datastore Sub-Type-4QueryStart',
								'zIntResou-Recipe ID-4QueryStart',
								'zAsset Complete',
								'zAsset-zPK',
								'zAddAssetAttr-zPK',
								'zAsset-UUID = store.cloudphotodb',
								'zAddAssetAttr-Master Fingerprint',
								'zIntResou-Fingerprint',
								'zAsset-Cloud is My Asset',
								'zAsset-Cloud is deletable/Asset',
								'zAsset-Cloud_Local_State',
								'zAsset-Visibility State',
								'zExtAttr-Camera Make',
								'zExtAttr-Camera Model',
								'zExtAttr-Lens Model',
								'zExtAttr-Flash Fired',
								'zExtAttr-Focal Lenght',
								'zAsset-Derived Camera Capture Device',
								'zAddAssetAttr-Camera Captured Device',
								'zAddAssetAttr-Imported by',
								'zCldMast-Imported By',
								'zAddAssetAttr-Creator Bundle ID',
								'zAddAssetAttr-Imported By Display Name',
								'zCldMast-Imported by Bundle ID',
								'zCldMast-Imported by Display Name',
								'zAsset-Saved Asset Type',
								'zAsset-Directory/Path',
								'zAsset-Filename',
								'zAddAssetAttr- Original Filename',
								'zCldMast- Original Filename',
								'zAsset-Added Date',
								'zAsset- SortToken -CameraRoll',
								'zAsset-Date Created',
								'zCldMast-Creation Date',
								'zIntResou-CldMst Date Created',
								'zAddAssetAttr-Time Zone Name',
								'zAddAssetAttr-Time Zone Offset',
								'zAddAssetAttr-Inferred Time Zone Offset',
								'zAddAssetAttr-EXIF-String',
								'zAsset-Modification Date',
								'zAsset-Last Shared Date',
								'zCldMast-Cloud Local State',
								'zCldMast-Import Date',
								'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
								'zAddAssetAttr-Import Session ID',
								'zAddAssetAttr-Alt Import Image Date',
								'zCldMast-Import Session ID- AirDrop-StillTesting',
								'zAsset-Cloud Batch Publish Date',
								'zAsset-Cloud Server Publish Date',
								'zAsset-Cloud Download Requests',
								'zAsset-Cloud Batch ID',
								'zAddAssetAttr-Upload Attempts',
								'zAsset-Latitude',
								'zExtAttr-Latitude',
								'zAsset-Longitude',
								'zExtAttr-Longitude',
								'zAddAssetAttr-GPS Horizontal Accuracy',
								'zAddAssetAttr-Location Hash',
								'zAddAssetAttr-Reverse Location Is Valid',
								'zAddAssetAttr-Shifted Location Valid',
								'AAAzCldMastMedData-zOPT',
								'zAddAssetAttr-Media Metadata Type',
								'CldMasterzCldMastMedData-zOPT',
								'zCldMast-Media Metadata Type',
								'zAsset-Orientation',
								'zAddAssetAttr-Original Orientation',
								'zAsset-Kind',
								'zAsset-Kind-Sub-Type',
								'zAddAssetAttr-Cloud Kind Sub Type',
								'zAsset-Playback Style',
								'zAsset-Playback Variation',
								'zAsset-Video Duration',
								'zExtAttr-Duration',
								'zAsset-Video CP Duration',
								'zAddAssetAttr-Video CP Duration Time Scale',
								'zAsset-Video CP Visibility State',
								'zAddAssetAttr-Video CP Display Value',
								'zAddAssetAttr-Video CP Display Time Scale',
								'zIntResou-Datastore Class ID',
								'zAsset-Cloud Placeholder Kind',
								'zIntResou-Local Availability',
								'zIntResou-Local Availability Target',
								'zIntResou-Cloud Local State',
								'zIntResou-Remote Availability',
								'zIntResou-Remote Availability Target',
								'zIntResou-Transient Cloud Master',
								'zIntResou-Side Car Index',
								'zIntResou- File ID',
								'zIntResou-Version',
								'zAddAssetAttr- Original-File-Size',
								'zIntResou-Resource Type',
								'zIntResou-Datastore Sub-Type',
								'zIntResou-Cloud Source Type',
								'zIntResou-Data Length',
								'zIntResou-Recipe ID',
								'zIntResou-Cloud Last Prefetch Date',
								'zIntResou-Cloud Prefetch Count',
								'zIntResou- Cloud-Last-OnDemand Download-Date',
								'zAsset-Uniform Type ID',
								'zAsset-Original Color Space',
								'zCldMast-Uniform_Type_ID',
								'zCldMast-Full Size JPEG Source',
								'zAsset-HDR Gain',
								'zExtAttr-Codec',
								'zCldMast-Codec Name',
								'zCldMast-Video Frame Rate',
								'zCldMast-Placeholder State',
								'zAsset-Depth_Type',
								'zAsset-Avalanche UUID',
								'zAsset-Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud Recovery State',
								'zAddAssetAttr-Cloud State Recovery Attempts Count',
								'zAsset-Deferred Processing Needed',
								'zAddAssetAttr-Deferred Photo Identifier',
								'zAddAssetAttr-Deferred Processing Candidate Options',
								'zAsset-Has Adjustments/Camera-Effects-Filters',
								'zAsset-Adjustment Timestamp',
								'zAddAssetAttr-Editor Bundle ID',
								'zAddAssetAttr-Montage',
								'zAsset-Favorite',
								'zAsset-Hidden',
								'zAsset-Trashed State/LocalAssetRecentlyDeleted',
								'zAsset-Trashed Date',
								'zIntResou-Trash State',
								'zIntResou-Trashed Date',
								'zAsset-Cloud Delete State',
								'zIntResou-Cloud Delete State',
								'zAddAssetAttr-PTP Trashed State',
								'zIntResou-PTP Trashed State',
								'zIntResou-Cloud Delete Asset UUID With Resource Type',
								'zMedAnlyAstAttr-Media Analysis Timestamp',
								'zAsset-Analysis State Modificaion Date',
								'zAddAssetAttr- Pending View Count',
								'zAddAssetAttr- View Count',
								'zAddAssetAttr- Pending Play Count',
								'zAddAssetAttr- Play Count',
								'zAddAssetAttr- Pending Share Count',
								'zAddAssetAttr- Share Count',
								'zAddAssetAttr-Allowed for Analysis',
								'zAddAssetAttr-Scene Analysis Version',
								'zAddAssetAttr-Scene Analysis Timestamp',
								'zAddAssetAttr-Destination Asset Copy State',
								'zAddAssetAttr-Variation Suggestions States',
								'zAsset-High Frame Rate State',
								'zAsset-Video Key Frame Time Scale',
								'zAsset-Video Key Frame Value',
								'zExtAttr-ISO',
								'zExtAttr-Metering Mode',
								'zExtAttr-Sample Rate',
								'zExtAttr-Track Format',
								'zExtAttr-White Balance',
								'zExtAttr-Aperture',
								'zExtAttr-BitRate',
								'zExtAttr-Exposure Bias',
								'zExtAttr-Frames Per Second',
								'zExtAttr-Shutter Speed',
								'zAsset-Height',
								'zAddAssetAttr-Original Height',
								'zIntResou-Unoriented Height',
								'zAsset-Width',
								'zAddAssetAttr-Original Width',
								'zIntResou-Unoriented Width',
								'zAsset-Thumbnail Index',
								'zAddAssetAttr-Embedded Thumbnail Height',
								'zAddAssetAttr-Embedded Thumbnail Length',
								'zAddAssetAttr-Embedded Thumbnail Offset',
								'zAddAssetAttr-Embedded Thumbnail Width',
								'zAsset-Packed Acceptable Crop Rect',
								'zAsset-Packed Badge Attributes',
								'zAsset-Packed Preferred Crop Rect',
								'zAsset-Curation Score',
								'zAsset-Camera Processing Adjustment State',
								'zAsset-Depth Type',
								'zAddAssetAttr-Orig Resource Choice',
								'zAddAssetAttr-Spatial Over Capture Group ID',
								'zAddAssetAttr-Place Annotation Data',
								'zAddAssetAttr-Edited IPTC Attributes',
								'zAddAssetAttr-Title/Comments via Cloud Website',
								'zAddAssetAttr-Accessibility Description',
								'zAddAssetAttr-Photo Stream Tag ID',
								'zAddAssetAttr-Share Type',
								'zAsset-Overall Aesthetic Score',
								'zAsset-zENT',
								'zAsset-zOPT',
								'zAsset-Master= zCldMast-zPK',
								'zAsset-Extended Attributes= zExtAttr-zPK',
								'zAsset-Import Session Key',
								'zAsset-FOK-Cloud Feed Asset Entry Key',
								'zAsset-Computed Attributes Asset Key',
								'zAsset-Promotion Score',
								'zAsset-Media Analysis Attributes Key',
								'zAsset-Media Group UUID',
								'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
								'zAsset.Cloud Collection GUID',
								'zAddAssetAttr-zENT',
								'ZAddAssetAttr-zOPT',
								'zAddAssetAttr-zAsset= zAsset_zPK',
								'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
								'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
								'zAddAssetAttr-Public Global UUID',
								'zAddAssetAttr-Original Assets UUID',
								'zAddAssetAttr-Originating Asset Identifier',
								'zAddAssetAttr.Adjusted Fingerprint',
								'zCldMast-zPK= zAsset-Master',
								'zCldMast-zENT',
								'zCldMast-zOPT',
								'zCldMast-Moment Share Key= zShare-zPK',
								'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
								'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
								'zCldMast-Originating Asset ID',
								'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
								'CMzCldMastMedData-zENT',
								'CMzCldMastMedData-CldMast= zCldMast-zPK',
								'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
								'AAAzCldMastMedData-zENT',
								'AAAzCldMastMedData-CldMast key',
								'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
								'zExtAttr-zPK= zAsset-zExtendedAttributes',
								'zExtAttr-zENT',
								'zExtAttr-zOPT',
								'zExtAttr-Asset Key',
								'zIntResou-zPK',
								'zIntResou-zENT',
								'zIntResou-zOPT',
								'zIntResou-Asset= zAsset_zPK',
								'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
								'zMedAnlyAstAttr-zEnt',
								'zMedAnlyAstAttr-zOpt',
								'zMedAnlyAstAttr-Asset= zAsset-zPK')
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = 'Ph50.2-Asset_IntResou-SyndPL'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = 'Ph50.2-Asset_IntResou-SyndPL'
				timeline(report_folder, tlactivity, data_list, data_headers)

			else:
				logfunc('No Internal Resource data available for iOS 14 Syndication Photos Library Photos.sqlite')

			db.close()
			return

		elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
			file_found = str(files_found[0])
			db = open_sqlite_db_readonly(file_found)
			cursor = db.cursor()

			cursor.execute("""
			SELECT
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability-4QueryStart',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability-4QueryStart',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type-4QueryStart',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID-4QueryStart',
			CASE zAsset.ZCOMPLETE
				WHEN 1 THEN '1-Yes-1'
			END AS 'zAsset Complete',
			zAsset.Z_PK AS 'zAsset-zPK',
			zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
			zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
			zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
			zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
			CASE zAsset.ZBUNDLESCOPE
				WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
				WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
				WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
				WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
			END AS 'zAsset-Bundle Scope',
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
			CASE zAsset.ZCLOUDISMYASSET
				WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
				WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
			END AS 'zAsset-Cloud is My Asset',
			CASE zAsset.ZCLOUDISDELETABLE
				WHEN 0 THEN '0-No-0'
				WHEN 1 THEN '1-Yes-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
			END AS 'zAsset-Cloud is deletable/Asset',
			CASE zAsset.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
				WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
			END AS 'zAsset-Cloud_Local_State',
			CASE zAsset.ZVISIBILITYSTATE
				WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
				WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
			END AS 'zAsset-Visibility State',
			zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
			zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
			zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
			CASE zExtAttr.ZFLASHFIRED
				WHEN 0 THEN '0-No Flash-0'
				WHEN 1 THEN '1-Flash Fired-1'
				ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
			END AS 'zExtAttr-Flash Fired',
			zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
			zExtAttr.ZFOCALLENGTHIN35MM AS 'zExtAttr-Focal Lenth in 35MM',
			zExtAttr.ZDIGITALZOOMRATIO AS 'zExtAttr-Digital Zoom Ratio',
			CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
			END AS 'zAsset-Derived Camera Capture Device',
			CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
			END AS 'zAddAssetAttr-Camera Captured Device',
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
			zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
			zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
			zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
			zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
			zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
			zAsset.ZFILENAME AS 'zAsset-Filename',
			zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
			zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
			zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
			DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
			DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
			CASE zAddAssetAttr.ZDATECREATEDSOURCE
				WHEN 0 THEN '0-Cloud-Asset-0'
				WHEN 1 THEN '1-Local_Asset_EXIF-1'
				WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
			END AS 'zAddAssetAttr-Date Created Source',
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
			DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
			DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
			zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
			zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
			zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
			zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
			DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
			DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
			CASE zCldMast.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-Not Synced with Cloud-0'
				WHEN 1 THEN '1-Pending Upload-1'
				WHEN 2 THEN '2-StillTesting'
				WHEN 3 THEN '3-Synced with Cloud-3'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
			END AS 'zCldMast-Cloud Local State',
			DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
			DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
			zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
			DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
			zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
			DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
			DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
			zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
			zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
			zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
			CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
				WHEN 0 THEN '0-Reverse Location Not Valid-0'
				WHEN 1 THEN '1-Reverse Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
			END AS 'zAddAssetAttr-Reverse Location Is Valid',
			CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
				WHEN 0 THEN '0-Shifted Location Not Valid-0'
				WHEN 1 THEN '1-Shifted Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
			END AS 'zAddAssetAttr-Shifted Location Valid',
			CASE AAAzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Cloud-1'
				WHEN 2 THEN '2-StillTesting-This Device-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
			END AS 'AAAzCldMastMedData-zOPT',
			zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
			CASE CMzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
				WHEN 2 THEN '2-StillTesting-Local_Asset-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
			END AS 'CldMasterzCldMastMedData-zOPT',
			zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
			zAddAssetAttr.ZSYNDICATIONHISTORY AS 'zAddAssetAttr-Syndication History',
			zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVERSION AS 'zMedAnlyAstAttr-Syndication Processing Version',
			CASE zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-STILLTESTING_Wide-Camera_JPG-1'
				WHEN 2 THEN '2-STILLTESTING_Telephoto_Camear_Lens-2'
				WHEN 4 THEN '4-STILLTESTING_SWY_Asset_OrigAssetImport_SystemPackageApp-4'
				WHEN 16 THEN '16-STILLTESTING-16'
				WHEN 1024 THEN '1024-STILLTESTING_SWY_Asset_OrigAssetImport_NativeCamera-1024'
				WHEN 2048 THEN '2048-STILLTESTING-2048'
				WHEN 4096 THEN '4096-STILLTESTING_SWY_Asset_Manually_Saved-4096'
				ELSE 'Unknown-New-Value!: ' || zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE || ''
			END AS 'zMedAnlyAstAttr-Syndication Processing Value',
			CASE zAsset.ZORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAsset-Orientation',
			CASE zAddAssetAttr.ZORIGINALORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAddAssetAttr-Original Orientation',
			CASE zAsset.ZKIND
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
			END AS 'zAsset-Kind',
			CASE zAsset.ZKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-Paorama-1'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
			END AS 'zAsset-Kind-Sub-Type',
			CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-StillTesting'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 3 THEN '3-Screenshot-3'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
			END AS 'zAddAssetAttr-Cloud Kind Sub Type',
			CASE zAsset.ZPLAYBACKSTYLE
				WHEN 1 THEN '1-Image-1'
				WHEN 2 THEN '2-Image-Animated-2'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 4 THEN '4-Video-4'
				WHEN 5 THEN '5-Video-Looping-5'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
			END AS 'zAsset-Playback Style',
			CASE zAsset.ZPLAYBACKVARIATION
				WHEN 0 THEN '0-No_Playback_Variation-0'
				WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
				WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
			END AS 'zAsset-Playback Variation',
			zAsset.ZDURATION AS 'zAsset-Video Duration',
			zExtAttr.ZDURATION AS 'zExtAttr-Duration',
			zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
			zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
			zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
			zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
			zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
			CASE zIntResou.ZDATASTORECLASSID
				WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
				WHEN 3 THEN '3-SWY_Syndication_Asset-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
			END AS 'zIntResou-Datastore Class ID',
			CASE zAsset.ZCLOUDPLACEHOLDERKIND
				WHEN 0 THEN '0-Local&CloudMaster Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-StillTesting-2'
				WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
				WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
				WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
				WHEN 6 THEN '6-StillTesting-6'
				WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
				WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
				WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
			END AS 'zAsset-Cloud Placeholder Kind',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability',
			CASE zIntResou.ZLOCALAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
			END AS 'zIntResou-Local Availability Target',
			CASE zIntResou.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
				WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
				WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
				WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
			END AS 'zIntResou-Cloud Local State',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability',
			CASE zIntResou.ZREMOTEAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				WHEN 1 THEN '1-StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
			END AS 'zIntResou-Remote Availability Target',
			zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
			zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
			zIntResou.ZFILEID AS 'zIntResou- File ID',
			CASE zIntResou.ZVERSION
				WHEN 0 THEN '0-IR_Asset_Standard-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
				WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
			END AS 'zIntResou-Version',
			zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type',
			CASE zIntResou.ZCLOUDSOURCETYPE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
			END AS 'zIntResou-Cloud Source Type',
			zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID',
			CASE zIntResou.ZCLOUDLASTPREFETCHDATE
				WHEN 0 THEN '0-NA-0'
				ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
			END AS 'zIntResou-Cloud Last Prefetch Date',
			zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
			DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
			CASE zIntResou.ZUTICONFORMANCEHINT
				WHEN 0 THEN '0-NA/Doesnt_Conform-0'
				WHEN 1 THEN '1-UTTypeImage-1'
				WHEN 2 THEN '2-UTTypeProRawPhoto-2'
				WHEN 3 THEN '3-UTTypeMovie-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
			END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
			CASE zIntResou.ZCOMPACTUTI
				WHEN 1 THEN '1-JPEG/THM-1'
				WHEN 3 THEN '3-HEIC-3'
				WHEN 6 THEN '6-PNG-6'
				WHEN 7 THEN '7-StillTesting'
				WHEN 9 THEN '9-DNG-9'
				WHEN 23 THEN '23-JPEG/HEIC/quicktime-mov-23'
				WHEN 24 THEN '24-MPEG4-24'
				WHEN 36 THEN '36-Wallpaper-36'
				WHEN 37 THEN '37-Adj/Mutation_Data-37'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCOMPACTUTI || ''
			END AS 'zIntResou-Compact-UTI',
			zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
			zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
			zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
			CASE zCldMast.ZFULLSIZEJPEGSOURCE
				WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
				WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
			END AS 'zCldMast-Full Size JPEG Source',
			zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
			CASE zAsset.ZHDRTYPE
				WHEN 0 THEN '0-No-HDR-0'
				WHEN 3 THEN '3-HDR_Photo-3_RT'
				WHEN 4 THEN '4-Non-HDR_Version-4_RT'
				WHEN 5 THEN '5-HEVC_Movie-5'
				WHEN 6 THEN '6-Panorama-6_RT'
				WHEN 10 THEN '10-HDR-Gain-10'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHDRTYPE || ''
			END AS 'zAsset-zHDR_Type',
			zExtAttr.ZCODEC AS 'zExtAttr-Codec',
			zIntResou.ZCODECFOURCHARCODENAME AS 'zIntResou-Codec Four Char Code Name',
			zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
			zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
			zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
			CASE zAsset.ZDEPTHTYPE
				WHEN 0 THEN '0-Not_Portrait-0_RT'
				ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
			END AS 'zAsset-Depth_Type',
			zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
			CASE zAsset.ZAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
			END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
			END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
				WHEN 0 THEN '0-StillTesting'
				WHEN 1 THEN '1-StillTesting'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
			END AS 'zAddAssetAttr-Cloud Recovery State',
			zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
			zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
			zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
			zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
			zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
			CASE zAsset.ZHASADJUSTMENTS
				WHEN 0 THEN '0-No-Adjustments-0'
				WHEN 1 THEN '1-Yes-Adjustments-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
			END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
			DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
			zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
			zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
			CASE zAsset.ZFAVORITE
				WHEN 0 THEN '0-Asset Not Favorite-0'
				WHEN 1 THEN '1-Asset Favorite-1'
			END AS 'zAsset-Favorite',
			CASE zAsset.ZHIDDEN
				WHEN 0 THEN '0-Asset Not Hidden-0'
				WHEN 1 THEN '1-Asset Hidden-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
			END AS 'zAsset-Hidden',
			CASE zAsset.ZTRASHEDSTATE
				WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
			END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
			DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
			CASE zIntResou.ZTRASHEDSTATE
				WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
			END AS 'zIntResou-Trash State',
			DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
			CASE zAsset.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
				WHEN 1 THEN '1-Cloud Asset Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
			END AS 'zAsset-Cloud Delete State',
			CASE zIntResou.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
				WHEN 1 THEN '1-Cloud IntResou Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
			END AS 'zIntResou-Cloud Delete State',
			CASE zAddAssetAttr.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP Not in Trash-0'
				WHEN 1 THEN '1-PTP In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
			END AS 'zAddAssetAttr-PTP Trashed State',
			CASE zIntResou.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
				WHEN 1 THEN '1-PTP IntResou In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
			END AS 'zIntResou-PTP Trashed State',
			zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
			DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
			DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
			zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
			zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
			zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
			zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
			zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
			zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
			CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
				WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
				WHEN 1 THEN '1-Asset Allowed for Analysis-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
			END AS 'zAddAssetAttr-Allowed for Analysis',
			zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
			CASE zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW
				WHEN 0 THEN '0-No-0'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW || ''
			END AS 'zAddAssetAttr-Scene Analysis is From Preview',
			DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
			CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
				WHEN 0 THEN '0-No Copy-0'
				WHEN 1 THEN '1-Has A Copy-1'
				WHEN 2 THEN '2-Has A Copy-2'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
			END AS 'zAddAssetAttr-Destination Asset Copy State',
			zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONSCOPEIDENTIFIER AS 'zAddAssetAttr-Source Asset for Duplication Scope ID',
			zCldMast.ZSOURCEMASTERFORDUPLICATIONSCOPEIDENTIFIER AS 'zCldMast-Source Master For Duplication Scope ID',
			zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONIDENTIFIER AS 'zAddAssetAttr-Source Asset For Duplication ID',
			zCldMast.ZSOURCEMASTERFORDUPLICATIONIDENTIFIER AS 'zCldMast-Source Master for Duplication ID',
			zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
			zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
			zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
			zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
			zExtAttr.ZISO AS 'zExtAttr-ISO',
			zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
			zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
			zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
			zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
			zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
			zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
			zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
			zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
			zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
			zExtAttr.ZSLUSHSCENEBIAS AS 'zExtAttr-Slush Scene Bias',
			zExtAttr.ZSLUSHVERSION AS 'zExtAttr-Slush Version',
			zExtAttr.ZSLUSHPRESET AS 'zExtAttr-Slush Preset',
			zExtAttr.ZSLUSHWARMTHBIAS AS 'zExtAttr-Slush Warm Bias',
			zAsset.ZHEIGHT AS 'zAsset-Height',
			zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
			zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
			zAsset.ZWIDTH AS 'zAsset-Width',
			zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
			zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
			zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
			zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
			zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
			zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
			zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
			zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
			zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
			zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',		
			CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
				WHEN 0 THEN '0-JPEG Original Resource-0'
				WHEN 1 THEN '1-RAW Original Resource-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
			END AS 'zAddAssetAttr-Orig Resource Choice',
			zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
			zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
			zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
			zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
			zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
			zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
			zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
			CASE zAddAssetAttr.ZSHARETYPE
				WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
				WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
			END AS 'zAddAssetAttr-Share Type',
			zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
			zAsset.Z_ENT AS 'zAsset-zENT',
			zAsset.Z_OPT AS 'zAsset-zOPT',
			zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
			zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
			zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
			zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
			zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
			zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
			zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
			zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
			zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
			zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
			zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
			zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
			zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
			zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
			zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
			zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
			zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
			zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
			zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
			zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
			zCldMast.Z_ENT AS 'zCldMast-zENT',
			zCldMast.Z_OPT AS 'zCldMast-zOPT',
			zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
			zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
			zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
			zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
			CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
			CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
			CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
			AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
			AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
			AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
			AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
			zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
			zExtAttr.Z_ENT AS 'zExtAttr-zENT',
			zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
			zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
			zIntResou.Z_PK AS 'zIntResou-zPK',
			zIntResou.Z_ENT AS 'zIntResou-zENT',
			zIntResou.Z_OPT AS 'zIntResou-zOPT',
			zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
			zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
			zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
			zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
			zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
			FROM ZASSET zAsset
				LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
				LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
				LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
				LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
				LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
				LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									  row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									  row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									  row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									  row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									  row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									  row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									  row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									  row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									  row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									  row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									  row[228], row[229], row[230], row[231], row[232], row[233], row[234], row[235],
									  row[236], row[237], row[238], row[239], row[240], row[241], row[242], row[243],
									  row[244], row[245], row[246], row[247], row[248], row[249], row[250], row[251],
									  row[252], row[253], row[254], row[255], row[256], row[257]))

					counter += 1

				description = 'Parses iOS 15 asset records from Syndication.photos.library/database/Photos.sqlite ZINTERNALRESOURCE and' \
							  ' other tables. This and other related parsers should provide data for investigative' \
							  ' analysis of assets being stored locally on the device verses assets being stored in' \
							  ' iCloud Photos as the result of optimization. This is very large query and script,' \
							  ' I recommend opening the TSV generated report with Zimmermans Tools' \
							  ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
							  ' and filter the results.'
				report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
				report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
				report.add_script()
				data_headers = ('zAsset-Date Created-4QueryStart',
								'zIntResou-Local Availability-4QueryStart',
								'zIntResou-Remote Availability-4QueryStart',
								'zIntResou-Resource Type-4QueryStart',
								'zIntResou-Datastore Sub-Type-4QueryStart',
								'zIntResou-Recipe ID-4QueryStart',
								'zAsset Complete',
								'zAsset-zPK',
								'zAddAssetAttr-zPK',
								'zAsset-UUID = store.cloudphotodb',
								'zAddAssetAttr-Master Fingerprint',
								'zIntResou-Fingerprint',
								'zAsset-Bundle Scope',
								'zAsset-Syndication State',
								'zAsset-Cloud is My Asset',
								'zAsset-Cloud is deletable/Asset',
								'zAsset-Cloud_Local_State',
								'zAsset-Visibility State',
								'zExtAttr-Camera Make',
								'zExtAttr-Camera Model',
								'zExtAttr-Lens Model',
								'zExtAttr-Flash Fired',
								'zExtAttr-Focal Lenght',
								'zExtAttr-Focal Lenth in 35MM',
								'zExtAttr-Digital Zoom Ratio',
								'zAsset-Derived Camera Capture Device',
								'zAddAssetAttr-Camera Captured Device',
								'zAddAssetAttr-Imported by',
								'zCldMast-Imported By',
								'zAddAssetAttr.Imported by Bundle Identifier',
								'zAddAssetAttr-Imported By Display Name',
								'zCldMast-Imported by Bundle ID',
								'zCldMast-Imported by Display Name',
								'zAsset-Saved Asset Type',
								'zAsset-Directory/Path',
								'zAsset-Filename',
								'zAddAssetAttr- Original Filename',
								'zCldMast- Original Filename',
								'zAddAssetAttr- Syndication Identifier-SWY-Files',
								'zAsset-Added Date',
								'zAsset- SortToken -CameraRoll',
								'zAddAssetAttr-Date Created Source',
								'zAsset-Date Created',
								'zCldMast-Creation Date',
								'zIntResou-CldMst Date Created',
								'zAddAssetAttr-Time Zone Name',
								'zAddAssetAttr-Time Zone Offset',
								'zAddAssetAttr-Inferred Time Zone Offset',
								'zAddAssetAttr-EXIF-String',
								'zAsset-Modification Date',
								'zAsset-Last Shared Date',
								'zCldMast-Cloud Local State',
								'zCldMast-Import Date',
								'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
								'zAddAssetAttr-Import Session ID',
								'zAddAssetAttr-Alt Import Image Date',
								'zCldMast-Import Session ID- AirDrop-StillTesting',
								'zAsset-Cloud Batch Publish Date',
								'zAsset-Cloud Server Publish Date',
								'zAsset-Cloud Download Requests',
								'zAsset-Cloud Batch ID',
								'zAddAssetAttr-Upload Attempts',
								'zAsset-Latitude',
								'zExtAttr-Latitude',
								'zAsset-Longitude',
								'zExtAttr-Longitude',
								'zAddAssetAttr-GPS Horizontal Accuracy',
								'zAddAssetAttr-Location Hash',
								'zAddAssetAttr-Reverse Location Is Valid',
								'zAddAssetAttr-Shifted Location Valid',
								'AAAzCldMastMedData-zOPT',
								'zAddAssetAttr-Media Metadata Type',
								'CldMasterzCldMastMedData-zOPT',
								'zCldMast-Media Metadata Type',
								'zAddAssetAttr-Syndication History',
								'zMedAnlyAstAttr-Syndication Processing Version',
								'zMedAnlyAstAttr-Syndication Processing Value',
								'zAsset-Orientation',
								'zAddAssetAttr-Original Orientation',
								'zAsset-Kind',
								'zAsset-Kind-Sub-Type',
								'zAddAssetAttr-Cloud Kind Sub Type',
								'zAsset-Playback Style',
								'zAsset-Playback Variation',
								'zAsset-Video Duration',
								'zExtAttr-Duration',
								'zAsset-Video CP Duration',
								'zAddAssetAttr-Video CP Duration Time Scale',
								'zAsset-Video CP Visibility State',
								'zAddAssetAttr-Video CP Display Value',
								'zAddAssetAttr-Video CP Display Time Scale',
								'zIntResou-Datastore Class ID',
								'zAsset-Cloud Placeholder Kind',
								'zIntResou-Local Availability',
								'zIntResou-Local Availability Target',
								'zIntResou-Cloud Local State',
								'zIntResou-Remote Availability',
								'zIntResou-Remote Availability Target',
								'zIntResou-Transient Cloud Master',
								'zIntResou-Side Car Index',
								'zIntResou- File ID',
								'zIntResou-Version',
								'zAddAssetAttr- Original-File-Size',
								'zIntResou-Resource Type',
								'zIntResou-Datastore Sub-Type',
								'zIntResou-Cloud Source Type',
								'zIntResou-Data Length',
								'zIntResou-Recipe ID',
								'zIntResou-Cloud Last Prefetch Date',
								'zIntResou-Cloud Prefetch Count',
								'zIntResou- Cloud-Last-OnDemand Download-Date',
								'zIntResou-UniformTypeID_UTI_Conformance_Hint',
								'zIntResou-Compact-UTI',
								'zAsset-Uniform Type ID',
								'zAsset-Original Color Space',
								'zCldMast-Uniform_Type_ID',
								'zCldMast-Full Size JPEG Source',
								'zAsset-HDR Gain',
								'zAsset-zHDR_Type',
								'zExtAttr-Codec',
								'zIntResou-Codec Four Char Code Name',
								'zCldMast-Codec Name',
								'zCldMast-Video Frame Rate',
								'zCldMast-Placeholder State',
								'zAsset-Depth_Type',
								'zAsset-Avalanche UUID',
								'zAsset-Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud Recovery State',
								'zAddAssetAttr-Cloud State Recovery Attempts Count',
								'zAsset-Deferred Processing Needed',
								'zAsset-Video Deferred Processing Needed',
								'zAddAssetAttr-Deferred Photo Identifier',
								'zAddAssetAttr-Deferred Processing Candidate Options',
								'zAsset-Has Adjustments/Camera-Effects-Filters',
								'zAsset-Adjustment Timestamp',
								'zAddAssetAttr-Editor Bundle ID',
								'zAddAssetAttr-Montage',
								'zAsset-Favorite',
								'zAsset-Hidden',
								'zAsset-Trashed State/LocalAssetRecentlyDeleted',
								'zAsset-Trashed Date',
								'zIntResou-Trash State',
								'zIntResou-Trashed Date',
								'zAsset-Cloud Delete State',
								'zIntResou-Cloud Delete State',
								'zAddAssetAttr-PTP Trashed State',
								'zIntResou-PTP Trashed State',
								'zIntResou-Cloud Delete Asset UUID With Resource Type',
								'zMedAnlyAstAttr-Media Analysis Timestamp',
								'zAsset-Analysis State Modificaion Date',
								'zAddAssetAttr- Pending View Count',
								'zAddAssetAttr- View Count',
								'zAddAssetAttr- Pending Play Count',
								'zAddAssetAttr- Play Count',
								'zAddAssetAttr- Pending Share Count',
								'zAddAssetAttr- Share Count',
								'zAddAssetAttr-Allowed for Analysis',
								'zAddAssetAttr-Scene Analysis Version',
								'zAddAssetAttr-Scene Analysis is From Preview',
								'zAddAssetAttr-Scene Analysis Timestamp',
								'zAddAssetAttr-Destination Asset Copy State',
								'zAddAssetAttr-Source Asset for Duplication Scope ID',
								'zCldMast-Source Master For Duplication Scope ID',
								'zAddAssetAttr-Source Asset For Duplication ID',
								'zCldMast-Source Master for Duplication ID',
								'zAddAssetAttr-Variation Suggestions States',
								'zAsset-High Frame Rate State',
								'zAsset-Video Key Frame Time Scale',
								'zAsset-Video Key Frame Value',
								'zExtAttr-ISO',
								'zExtAttr-Metering Mode',
								'zExtAttr-Sample Rate',
								'zExtAttr-Track Format',
								'zExtAttr-White Balance',
								'zExtAttr-Aperture',
								'zExtAttr-BitRate',
								'zExtAttr-Exposure Bias',
								'zExtAttr-Frames Per Second',
								'zExtAttr-Shutter Speed',
								'zExtAttr-Slush Scene Bias',
								'zExtAttr-Slush Version',
								'zExtAttr-Slush Preset',
								'zExtAttr-Slush Warm Bias',
								'zAsset-Height',
								'zAddAssetAttr-Original Height',
								'zIntResou-Unoriented Height',
								'zAsset-Width',
								'zAddAssetAttr-Original Width',
								'zIntResou-Unoriented Width',
								'zAsset-Thumbnail Index',
								'zAddAssetAttr-Embedded Thumbnail Height',
								'zAddAssetAttr-Embedded Thumbnail Length',
								'zAddAssetAttr-Embedded Thumbnail Offset',
								'zAddAssetAttr-Embedded Thumbnail Width',
								'zAsset-Packed Acceptable Crop Rect',
								'zAsset-Packed Badge Attributes',
								'zAsset-Packed Preferred Crop Rect',
								'zAsset-Curation Score',
								'zAsset-Camera Processing Adjustment State',
								'zAsset-Depth Type',
								'zAsset-Is Magic Carpet-QuicktimeMOVfile',
								'zAddAssetAttr-Orig Resource Choice',
								'zAddAssetAttr-Spatial Over Capture Group ID',
								'zAddAssetAttr-Place Annotation Data',
								'zAddAssetAttr-Edited IPTC Attributes',
								'zAddAssetAttr-Title/Comments via Cloud Website',
								'zAddAssetAttr-Accessibility Description',
								'zAddAssetAttr-Photo Stream Tag ID',
								'zAddAssetAttr-Share Type',
								'zAsset-Overall Aesthetic Score',
								'zAsset-zENT',
								'zAsset-zOPT',
								'zAsset-Master= zCldMast-zPK',
								'zAsset-Extended Attributes= zExtAttr-zPK',
								'zAsset-Import Session Key',
								'zAsset-FOK-Cloud Feed Asset Entry Key',
								'zAsset-Computed Attributes Asset Key',
								'zAsset-Promotion Score',
								'zAsset-Media Analysis Attributes Key',
								'zAsset-Media Group UUID',
								'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
								'zAsset.Cloud Collection GUID',
								'zAddAssetAttr-zENT',
								'ZAddAssetAttr-zOPT',
								'zAddAssetAttr-zAsset= zAsset_zPK',
								'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
								'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
								'zAddAssetAttr-Public Global UUID',
								'zAddAssetAttr-Original Assets UUID',
								'zAddAssetAttr-Originating Asset Identifier',
								'zAddAssetAttr.Adjusted Fingerprint',
								'zCldMast-zPK= zAsset-Master',
								'zCldMast-zENT',
								'zCldMast-zOPT',
								'zCldMast-Moment Share Key= zShare-zPK',
								'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
								'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
								'zCldMast-Originating Asset ID',
								'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
								'CMzCldMastMedData-zENT',
								'CMzCldMastMedData-CldMast= zCldMast-zPK',
								'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
								'AAAzCldMastMedData-zENT',
								'AAAzCldMastMedData-CldMast key',
								'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
								'zExtAttr-zPK= zAsset-zExtendedAttributes',
								'zExtAttr-zENT',
								'zExtAttr-zOPT',
								'zExtAttr-Asset Key',
								'zIntResou-zPK',
								'zIntResou-zENT',
								'zIntResou-zOPT',
								'zIntResou-Asset= zAsset_zPK',
								'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
								'zMedAnlyAstAttr-zEnt',
								'zMedAnlyAstAttr-zOpt',
								'zMedAnlyAstAttr-Asset= zAsset-zPK')
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = 'Ph50.2-Asset_IntResou-SyndPL'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = 'Ph50.2-Asset_IntResou-SyndPL'
				timeline(report_folder, tlactivity, data_list, data_headers)

			else:
				logfunc('No Internal Resource data available for iOS 15 Syndication Photos Library Photos.sqlite')

			db.close()
			return

		elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
			file_found = str(files_found[0])
			db = open_sqlite_db_readonly(file_found)
			cursor = db.cursor()

			cursor.execute("""
			SELECT
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability-4QueryStart',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability-4QueryStart',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type-4QueryStart',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID-4QueryStart',
			CASE zAsset.ZCOMPLETE
				WHEN 1 THEN '1-Yes-1'
			END AS 'zAsset Complete',
			zAsset.Z_PK AS 'zAsset-zPK',
			zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
			zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
			zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
			zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
			CASE zAsset.ZBUNDLESCOPE
				WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
				WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
				WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
				WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
			END AS 'zAsset-Bundle Scope',
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
			CASE zAsset.ZCLOUDISMYASSET
				WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
				WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
			END AS 'zAsset-Cloud is My Asset',
			CASE zAsset.ZCLOUDISDELETABLE
				WHEN 0 THEN '0-No-0'
				WHEN 1 THEN '1-Yes-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
			END AS 'zAsset-Cloud is deletable/Asset',
			CASE zAsset.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
				WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
			END AS 'zAsset-Cloud_Local_State',
			CASE zAsset.ZVISIBILITYSTATE
				WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
				WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
			END AS 'zAsset-Visibility State',
			zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
			zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
			zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
			CASE zExtAttr.ZFLASHFIRED
				WHEN 0 THEN '0-No Flash-0'
				WHEN 1 THEN '1-Flash Fired-1'
				ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
			END AS 'zExtAttr-Flash Fired',
			zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
			zExtAttr.ZFOCALLENGTHIN35MM AS 'zExtAttr-Focal Lenth in 35MM',
			zExtAttr.ZDIGITALZOOMRATIO AS 'zExtAttr-Digital Zoom Ratio',
			CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
			END AS 'zAsset-Derived Camera Capture Device',
			CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
			END AS 'zAddAssetAttr-Camera Captured Device',
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
			zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
			zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
			zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
			zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
			zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
			zAsset.ZFILENAME AS 'zAsset-Filename',
			zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
			zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
			zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
			CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
				WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
				WHEN 1 THEN '1-Asset-In-Active-SPL-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
			END AS 'zAsset-Active Library Scope Participation State',
			CASE zAsset.ZLIBRARYSCOPESHARESTATE
				WHEN 0 THEN '0-Asset-Not-In-SPL-0'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
			END AS 'zAsset-Library Scope Share State- StillTesting',
			DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
			DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
			CASE zAddAssetAttr.ZDATECREATEDSOURCE
				WHEN 0 THEN '0-Cloud-Asset-0'
				WHEN 1 THEN '1-Local_Asset_EXIF-1'
				WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
			END AS 'zAddAssetAttr-Date Created Source',
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
			DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
			DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
			zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
			zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
			zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
			zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
			DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
			DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
			DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
			CASE zCldMast.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-Not Synced with Cloud-0'
				WHEN 1 THEN '1-Pending Upload-1'
				WHEN 2 THEN '2-StillTesting'
				WHEN 3 THEN '3-Synced with Cloud-3'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
			END AS 'zCldMast-Cloud Local State',
			DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
			DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
			zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
			DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
			zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
			DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
			DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
			zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
			zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
			zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
			CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
				WHEN 0 THEN '0-Reverse Location Not Valid-0'
				WHEN 1 THEN '1-Reverse Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
			END AS 'zAddAssetAttr-Reverse Location Is Valid',
			CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
				WHEN 0 THEN '0-Shifted Location Not Valid-0'
				WHEN 1 THEN '1-Shifted Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
			END AS 'zAddAssetAttr-Shifted Location Valid',
			CASE AAAzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Cloud-1'
				WHEN 2 THEN '2-StillTesting-This Device-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
			END AS 'AAAzCldMastMedData-zOPT',
			zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
			CASE CMzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
				WHEN 2 THEN '2-StillTesting-Local_Asset-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
			END AS 'CldMasterzCldMastMedData-zOPT',
			zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
			CASE zAsset.ZSEARCHINDEXREBUILDSTATE
				WHEN 0 THEN '0-StillTesting-0'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZSEARCHINDEXREBUILDSTATE || ''
			END AS 'zAsset-Search Index Rebuild State',
			zAddAssetAttr.ZSYNDICATIONHISTORY AS 'zAddAssetAttr-Syndication History',
			zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVERSION AS 'zMedAnlyAstAttr-Syndication Processing Version',
			CASE zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-STILLTESTING_Wide-Camera_JPG-1'
				WHEN 2 THEN '2-STILLTESTING_Telephoto_Camear_Lens-2'
				WHEN 4 THEN '4-STILLTESTING_SWY_Asset_OrigAssetImport_SystemPackageApp-4'
				WHEN 16 THEN '16-STILLTESTING-16'
				WHEN 1024 THEN '1024-STILLTESTING_SWY_Asset_OrigAssetImport_NativeCamera-1024'
				WHEN 2048 THEN '2048-STILLTESTING-2048'
				WHEN 4096 THEN '4096-STILLTESTING_SWY_Asset_Manually_Saved-4096'
				ELSE 'Unknown-New-Value!: ' || zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE || ''
			END AS 'zMedAnlyAstAttr-Syndication Processing Value',
			CASE zAsset.ZORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAsset-Orientation',
			CASE zAddAssetAttr.ZORIGINALORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAddAssetAttr-Original Orientation',
			CASE zAsset.ZKIND
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
			END AS 'zAsset-Kind',
			CASE zAsset.ZKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-Paorama-1'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
			END AS 'zAsset-Kind-Sub-Type',
			CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-StillTesting'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 3 THEN '3-Screenshot-3'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
			END AS 'zAddAssetAttr-Cloud Kind Sub Type',
			CASE zAsset.ZPLAYBACKSTYLE
				WHEN 1 THEN '1-Image-1'
				WHEN 2 THEN '2-Image-Animated-2'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 4 THEN '4-Video-4'
				WHEN 5 THEN '5-Video-Looping-5'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
			END AS 'zAsset-Playback Style',
			CASE zAsset.ZPLAYBACKVARIATION
				WHEN 0 THEN '0-No_Playback_Variation-0'
				WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
				WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
			END AS 'zAsset-Playback Variation',
			zAsset.ZDURATION AS 'zAsset-Video Duration',
			zExtAttr.ZDURATION AS 'zExtAttr-Duration',
			zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
			zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
			zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
			zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
			zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
			CASE zIntResou.ZDATASTORECLASSID
				WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
				WHEN 3 THEN '3-SWY_Syndication_Asset-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
			END AS 'zIntResou-Datastore Class ID',
			CASE zAsset.ZCLOUDPLACEHOLDERKIND
				WHEN 0 THEN '0-Local&CloudMaster Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-StillTesting-2'
				WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
				WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
				WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
				WHEN 6 THEN '6-StillTesting-6'
				WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
				WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
				WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
			END AS 'zAsset-Cloud Placeholder Kind',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability',
			CASE zIntResou.ZLOCALAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
			END AS 'zIntResou-Local Availability Target',
			CASE zIntResou.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
				WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
				WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
				WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
			END AS 'zIntResou-Cloud Local State',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability',
			CASE zIntResou.ZREMOTEAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				WHEN 1 THEN '1-StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
			END AS 'zIntResou-Remote Availability Target',
			zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
			zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
			zIntResou.ZFILEID AS 'zIntResou- File ID',
			CASE zIntResou.ZVERSION
				WHEN 0 THEN '0-IR_Asset_Standard-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
				WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
			END AS 'zIntResou-Version',
			zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type',
			CASE zIntResou.ZCLOUDSOURCETYPE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
			END AS 'zIntResou-Cloud Source Type',
			zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID',
			CASE zIntResou.ZCLOUDLASTPREFETCHDATE
				WHEN 0 THEN '0-NA-0'
				ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
			END AS 'zIntResou-Cloud Last Prefetch Date',
			zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
			DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
			CASE zIntResou.ZUTICONFORMANCEHINT
				WHEN 0 THEN '0-NA/Doesnt_Conform-0'
				WHEN 1 THEN '1-UTTypeImage-1'
				WHEN 2 THEN '2-UTTypeProRawPhoto-2'
				WHEN 3 THEN '3-UTTypeMovie-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
			END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
			CASE zIntResou.ZCOMPACTUTI
				WHEN 1 THEN '1-JPEG/THM-1'
				WHEN 3 THEN '3-HEIC-3'
				WHEN 6 THEN '6-PNG-6'
				WHEN 7 THEN '7-StillTesting'
				WHEN 9 THEN '9-DNG-9'
				WHEN 23 THEN '23-JPEG/HEIC/quicktime-mov-23'
				WHEN 24 THEN '24-MPEG4-24'
				WHEN 36 THEN '36-Wallpaper-36'
				WHEN 37 THEN '37-Adj/Mutation_Data-37'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCOMPACTUTI || ''
			END AS 'zIntResou-Compact-UTI',
			zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
			zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
			zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
			CASE zCldMast.ZFULLSIZEJPEGSOURCE
				WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
				WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
			END AS 'zCldMast-Full Size JPEG Source',
			zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
			CASE zAsset.ZHDRTYPE
				WHEN 0 THEN '0-No-HDR-0'
				WHEN 3 THEN '3-HDR_Photo-3_RT'
				WHEN 4 THEN '4-Non-HDR_Version-4_RT'
				WHEN 5 THEN '5-HEVC_Movie-5'
				WHEN 6 THEN '6-Panorama-6_RT'
				WHEN 10 THEN '10-HDR-Gain-10'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHDRTYPE || ''
			END AS 'zAsset-zHDR_Type',
			zExtAttr.ZCODEC AS 'zExtAttr-Codec',
			zIntResou.ZCODECFOURCHARCODENAME AS 'zIntResou-Codec Four Char Code Name',
			zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
			zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
			zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
			CASE zAsset.ZDEPTHTYPE
				WHEN 0 THEN '0-Not_Portrait-0_RT'
				ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
			END AS 'zAsset-Depth_Type',
			zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
			CASE zAsset.ZAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
			END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
			END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
				WHEN 0 THEN '0-StillTesting'
				WHEN 1 THEN '1-StillTesting'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
			END AS 'zAddAssetAttr-Cloud Recovery State',
			zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
			zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
			zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
			zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
			zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
			CASE zAsset.ZHASADJUSTMENTS
				WHEN 0 THEN '0-No-Adjustments-0'
				WHEN 1 THEN '1-Yes-Adjustments-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
			END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
			DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
			zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
			zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
			CASE zAsset.ZFAVORITE
				WHEN 0 THEN '0-Asset Not Favorite-0'
				WHEN 1 THEN '1-Asset Favorite-1'
			END AS 'zAsset-Favorite',
			CASE zAsset.ZHIDDEN
				WHEN 0 THEN '0-Asset Not Hidden-0'
				WHEN 1 THEN '1-Asset Hidden-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
			END AS 'zAsset-Hidden',
			CASE zAsset.ZTRASHEDSTATE
				WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
			END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
			DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
			zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
			CASE zAsset.ZDELETEREASON
				WHEN 1 THEN '1-StillTesting Delete-Reason-1'
				WHEN 2 THEN '2-StillTesting Delete-Reason-2'
				WHEN 3 THEN '3-StillTesting Delete-Reason-3'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
			END AS 'zAsset-Delete-Reason',
			CASE zIntResou.ZTRASHEDSTATE
				WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
			END AS 'zIntResou-Trash State',
			DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
			CASE zAsset.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
				WHEN 1 THEN '1-Cloud Asset Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
			END AS 'zAsset-Cloud Delete State',
			CASE zIntResou.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
				WHEN 1 THEN '1-Cloud IntResou Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
			END AS 'zIntResou-Cloud Delete State',
			CASE zAddAssetAttr.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP Not in Trash-0'
				WHEN 1 THEN '1-PTP In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
			END AS 'zAddAssetAttr-PTP Trashed State',
			CASE zIntResou.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
				WHEN 1 THEN '1-PTP IntResou In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
			END AS 'zIntResou-PTP Trashed State',
			zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
			DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
			DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
			zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
			zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
			zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
			zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
			zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
			zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
			CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
				WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
				WHEN 1 THEN '1-Asset Allowed for Analysis-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
			END AS 'zAddAssetAttr-Allowed for Analysis',
			zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
			CASE zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW
				WHEN 0 THEN '0-No-0'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW || ''
			END AS 'zAddAssetAttr-Scene Analysis is From Preview',
			DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
			CASE zAsset.ZDUPLICATEASSETVISIBILITYSTATE
				WHEN 0 THEN '0-No-Duplicates-0'
				WHEN 1 THEN '1-Has Duplicate-1'
				WHEN 2 THEN '2-Is a Duplicate-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDUPLICATEASSETVISIBILITYSTATE || ''
			END AS 'zAsset-Duplication Asset Visibility State',
			CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
				WHEN 0 THEN '0-No Copy-0'
				WHEN 1 THEN '1-Has A Copy-1'
				WHEN 2 THEN '2-Has A Copy-2'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
			END AS 'zAddAssetAttr-Destination Asset Copy State',
			CASE zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE
				WHEN 0 THEN '0-Unknown-StillTesting-0'
				WHEN 1 THEN '1-Unknown-StillTesting-1'
				WHEN 2 THEN '2-Unknown-StillTesting-2'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE || ''
			END AS 'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
			zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONSCOPEIDENTIFIER AS 'zAddAssetAttr-Source Asset for Duplication Scope ID',
			zCldMast.ZSOURCEMASTERFORDUPLICATIONSCOPEIDENTIFIER AS 'zCldMast-Source Master For Duplication Scope ID',
			zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONIDENTIFIER AS 'zAddAssetAttr-Source Asset For Duplication ID',
			zCldMast.ZSOURCEMASTERFORDUPLICATIONIDENTIFIER AS 'zCldMast-Source Master for Duplication ID',
			zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
			zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
			zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
			zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
			zExtAttr.ZISO AS 'zExtAttr-ISO',
			zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
			zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
			zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
			zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
			zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
			zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
			zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
			zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
			zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
			zExtAttr.ZSLUSHSCENEBIAS AS 'zExtAttr-Slush Scene Bias',
			zExtAttr.ZSLUSHVERSION AS 'zExtAttr-Slush Version',
			zExtAttr.ZSLUSHPRESET AS 'zExtAttr-Slush Preset',
			zExtAttr.ZSLUSHWARMTHBIAS AS 'zExtAttr-Slush Warm Bias',
			zAsset.ZHEIGHT AS 'zAsset-Height',
			zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
			zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
			zAsset.ZWIDTH AS 'zAsset-Width',
			zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
			zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
			zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
			zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
			zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
			zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
			zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
			zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
			zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
			zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',		
			CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
				WHEN 0 THEN '0-JPEG Original Resource-0'
				WHEN 1 THEN '1-RAW Original Resource-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
			END AS 'zAddAssetAttr-Orig Resource Choice',
			zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
			zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
			zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
			zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
			zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
			zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
			zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
			CASE zAddAssetAttr.ZSHARETYPE
				WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
				WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
			END AS 'zAddAssetAttr-Share Type',
			zAddAssetAttr.ZLIBRARYSCOPEASSETCONTRIBUTORSTOUPDATE AS 'zAddAssetAttr-Library Scope Asset Contributors To Update',
			zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
			zAsset.Z_ENT AS 'zAsset-zENT',
			zAsset.Z_OPT AS 'zAsset-zOPT',
			zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
			zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
			zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
			zAsset.ZPHOTOANALYSISATTRIBUTES AS 'zAsset-Photo Analysis Attributes Key',
			zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
			zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
			zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
			zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
			zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
			zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
			zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
			zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
			zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
			zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
			zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
			zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
			zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
			zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
			zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
			zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
			zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
			zCldMast.Z_ENT AS 'zCldMast-zENT',
			zCldMast.Z_OPT AS 'zCldMast-zOPT',
			zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
			zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
			zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
			zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
			CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
			CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
			CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
			AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
			AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
			AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
			AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
			zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
			zExtAttr.Z_ENT AS 'zExtAttr-zENT',
			zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
			zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
			zIntResou.Z_PK AS 'zIntResou-zPK',
			zIntResou.Z_ENT AS 'zIntResou-zENT',
			zIntResou.Z_OPT AS 'zIntResou-zOPT',
			zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
			zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
			zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
			zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
			zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
			FROM ZASSET zAsset
				LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
				LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
				LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
				LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
				LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
				LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									  row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									  row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									  row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									  row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									  row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									  row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									  row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									  row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									  row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									  row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									  row[228], row[229], row[230], row[231], row[232], row[233], row[234], row[235],
									  row[236], row[237], row[238], row[239], row[240], row[241], row[242], row[243],
									  row[244], row[245], row[246], row[247], row[248], row[249], row[250], row[251],
									  row[252], row[253], row[254], row[255], row[256], row[257], row[258], row[259],
									  row[260], row[261], row[262], row[263], row[264], row[265], row[266], row[267]))

					counter += 1

				description = 'Parses iOS 16 asset records from Syndication.photos.library/database/Photos.sqlite ZINTERNALRESOURCE and' \
							  ' other tables. This and other related parsers should provide data for investigative' \
							  ' analysis of assets being stored locally on the device verses assets being stored in' \
							  ' iCloud Photos as the result of optimization. This is very large query and script,' \
							  ' I recommend opening the TSV generated report with Zimmermans Tools' \
							  ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
							  ' and filter the results.'
				report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
				report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
				report.add_script()
				data_headers = ('zAsset-Date Created-4QueryStart',
								'zIntResou-Local Availability-4QueryStart',
								'zIntResou-Remote Availability-4QueryStart',
								'zIntResou-Resource Type-4QueryStart',
								'zIntResou-Datastore Sub-Type-4QueryStart',
								'zIntResou-Recipe ID-4QueryStart',
								'zAsset Complete',
								'zAsset-zPK',
								'zAddAssetAttr-zPK',
								'zAsset-UUID = store.cloudphotodb',
								'zAddAssetAttr-Master Fingerprint',
								'zIntResou-Fingerprint',
								'zAsset-Bundle Scope',
								'zAsset-Syndication State',
								'zAsset-Cloud is My Asset',
								'zAsset-Cloud is deletable/Asset',
								'zAsset-Cloud_Local_State',
								'zAsset-Visibility State',
								'zExtAttr-Camera Make',
								'zExtAttr-Camera Model',
								'zExtAttr-Lens Model',
								'zExtAttr-Flash Fired',
								'zExtAttr-Focal Lenght',
								'zExtAttr-Focal Lenth in 35MM',
								'zExtAttr-Digital Zoom Ratio',
								'zAsset-Derived Camera Capture Device',
								'zAddAssetAttr-Camera Captured Device',
								'zAddAssetAttr-Imported by',
								'zCldMast-Imported By',
								'zAddAssetAttr.Imported by Bundle Identifier',
								'zAddAssetAttr-Imported By Display Name',
								'zCldMast-Imported by Bundle ID',
								'zCldMast-Imported by Display Name',
								'zAsset-Saved Asset Type',
								'zAsset-Directory/Path',
								'zAsset-Filename',
								'zAddAssetAttr- Original Filename',
								'zCldMast- Original Filename',
								'zAddAssetAttr- Syndication Identifier-SWY-Files',
								'zAsset-Active Library Scope Participation State',
								'zAsset-Library Scope Share State- StillTesting',
								'zAsset-Added Date',
								'zAsset- SortToken -CameraRoll',
								'zAddAssetAttr-Date Created Source',
								'zAsset-Date Created',
								'zCldMast-Creation Date',
								'zIntResou-CldMst Date Created',
								'zAddAssetAttr-Time Zone Name',
								'zAddAssetAttr-Time Zone Offset',
								'zAddAssetAttr-Inferred Time Zone Offset',
								'zAddAssetAttr-EXIF-String',
								'zAsset-Modification Date',
								'zAddAssetAttr-Last Viewed Date',
								'zAsset-Last Shared Date',
								'zCldMast-Cloud Local State',
								'zCldMast-Import Date',
								'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
								'zAddAssetAttr-Import Session ID',
								'zAddAssetAttr-Alt Import Image Date',
								'zCldMast-Import Session ID- AirDrop-StillTesting',
								'zAsset-Cloud Batch Publish Date',
								'zAsset-Cloud Server Publish Date',
								'zAsset-Cloud Download Requests',
								'zAsset-Cloud Batch ID',
								'zAddAssetAttr-Upload Attempts',
								'zAsset-Latitude',
								'zExtAttr-Latitude',
								'zAsset-Longitude',
								'zExtAttr-Longitude',
								'zAddAssetAttr-GPS Horizontal Accuracy',
								'zAddAssetAttr-Location Hash',
								'zAddAssetAttr-Reverse Location Is Valid',
								'zAddAssetAttr-Shifted Location Valid',
								'AAAzCldMastMedData-zOPT',
								'zAddAssetAttr-Media Metadata Type',
								'CldMasterzCldMastMedData-zOPT',
								'zCldMast-Media Metadata Type',
								'zAsset-Search Index Rebuild State',
								'zAddAssetAttr-Syndication History',
								'zMedAnlyAstAttr-Syndication Processing Version',
								'zMedAnlyAstAttr-Syndication Processing Value',
								'zAsset-Orientation',
								'zAddAssetAttr-Original Orientation',
								'zAsset-Kind',
								'zAsset-Kind-Sub-Type',
								'zAddAssetAttr-Cloud Kind Sub Type',
								'zAsset-Playback Style',
								'zAsset-Playback Variation',
								'zAsset-Video Duration',
								'zExtAttr-Duration',
								'zAsset-Video CP Duration',
								'zAddAssetAttr-Video CP Duration Time Scale',
								'zAsset-Video CP Visibility State',
								'zAddAssetAttr-Video CP Display Value',
								'zAddAssetAttr-Video CP Display Time Scale',
								'zIntResou-Datastore Class ID',
								'zAsset-Cloud Placeholder Kind',
								'zIntResou-Local Availability',
								'zIntResou-Local Availability Target',
								'zIntResou-Cloud Local State',
								'zIntResou-Remote Availability',
								'zIntResou-Remote Availability Target',
								'zIntResou-Transient Cloud Master',
								'zIntResou-Side Car Index',
								'zIntResou- File ID',
								'zIntResou-Version',
								'zAddAssetAttr- Original-File-Size',
								'zIntResou-Resource Type',
								'zIntResou-Datastore Sub-Type',
								'zIntResou-Cloud Source Type',
								'zIntResou-Data Length',
								'zIntResou-Recipe ID',
								'zIntResou-Cloud Last Prefetch Date',
								'zIntResou-Cloud Prefetch Count',
								'zIntResou- Cloud-Last-OnDemand Download-Date',
								'zIntResou-UniformTypeID_UTI_Conformance_Hint',
								'zIntResou-Compact-UTI',
								'zAsset-Uniform Type ID',
								'zAsset-Original Color Space',
								'zCldMast-Uniform_Type_ID',
								'zCldMast-Full Size JPEG Source',
								'zAsset-HDR Gain',
								'zAsset-zHDR_Type',
								'zExtAttr-Codec',
								'zIntResou-Codec Four Char Code Name',
								'zCldMast-Codec Name',
								'zCldMast-Video Frame Rate',
								'zCldMast-Placeholder State',
								'zAsset-Depth_Type',
								'zAsset-Avalanche UUID',
								'zAsset-Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud Recovery State',
								'zAddAssetAttr-Cloud State Recovery Attempts Count',
								'zAsset-Deferred Processing Needed',
								'zAsset-Video Deferred Processing Needed',
								'zAddAssetAttr-Deferred Photo Identifier',
								'zAddAssetAttr-Deferred Processing Candidate Options',
								'zAsset-Has Adjustments/Camera-Effects-Filters',
								'zAsset-Adjustment Timestamp',
								'zAddAssetAttr-Editor Bundle ID',
								'zAddAssetAttr-Montage',
								'zAsset-Favorite',
								'zAsset-Hidden',
								'zAsset-Trashed State/LocalAssetRecentlyDeleted',
								'zAsset-Trashed Date',
								'zAsset-Trashed by Participant= zSharePartic_zPK',
								'zAsset-Delete-Reason',
								'zIntResou-Trash State',
								'zIntResou-Trashed Date',
								'zAsset-Cloud Delete State',
								'zIntResou-Cloud Delete State',
								'zAddAssetAttr-PTP Trashed State',
								'zIntResou-PTP Trashed State',
								'zIntResou-Cloud Delete Asset UUID With Resource Type',
								'zMedAnlyAstAttr-Media Analysis Timestamp',
								'zAsset-Analysis State Modificaion Date',
								'zAddAssetAttr- Pending View Count',
								'zAddAssetAttr- View Count',
								'zAddAssetAttr- Pending Play Count',
								'zAddAssetAttr- Play Count',
								'zAddAssetAttr- Pending Share Count',
								'zAddAssetAttr- Share Count',
								'zAddAssetAttr-Allowed for Analysis',
								'zAddAssetAttr-Scene Analysis Version',
								'zAddAssetAttr-Scene Analysis is From Preview',
								'zAddAssetAttr-Scene Analysis Timestamp',
								'zAsset-Duplication Asset Visibility State',
								'zAddAssetAttr-Destination Asset Copy State',
								'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
								'zAddAssetAttr-Source Asset for Duplication Scope ID',
								'zCldMast-Source Master For Duplication Scope ID',
								'zAddAssetAttr-Source Asset For Duplication ID',
								'zCldMast-Source Master for Duplication ID',
								'zAddAssetAttr-Variation Suggestions States',
								'zAsset-High Frame Rate State',
								'zAsset-Video Key Frame Time Scale',
								'zAsset-Video Key Frame Value',
								'zExtAttr-ISO',
								'zExtAttr-Metering Mode',
								'zExtAttr-Sample Rate',
								'zExtAttr-Track Format',
								'zExtAttr-White Balance',
								'zExtAttr-Aperture',
								'zExtAttr-BitRate',
								'zExtAttr-Exposure Bias',
								'zExtAttr-Frames Per Second',
								'zExtAttr-Shutter Speed',
								'zExtAttr-Slush Scene Bias',
								'zExtAttr-Slush Version',
								'zExtAttr-Slush Preset',
								'zExtAttr-Slush Warm Bias',
								'zAsset-Height',
								'zAddAssetAttr-Original Height',
								'zIntResou-Unoriented Height',
								'zAsset-Width',
								'zAddAssetAttr-Original Width',
								'zIntResou-Unoriented Width',
								'zAsset-Thumbnail Index',
								'zAddAssetAttr-Embedded Thumbnail Height',
								'zAddAssetAttr-Embedded Thumbnail Length',
								'zAddAssetAttr-Embedded Thumbnail Offset',
								'zAddAssetAttr-Embedded Thumbnail Width',
								'zAsset-Packed Acceptable Crop Rect',
								'zAsset-Packed Badge Attributes',
								'zAsset-Packed Preferred Crop Rect',
								'zAsset-Curation Score',
								'zAsset-Camera Processing Adjustment State',
								'zAsset-Depth Type',
								'zAsset-Is Magic Carpet-QuicktimeMOVfile',
								'zAddAssetAttr-Orig Resource Choice',
								'zAddAssetAttr-Spatial Over Capture Group ID',
								'zAddAssetAttr-Place Annotation Data',
								'zAddAssetAttr-Edited IPTC Attributes',
								'zAddAssetAttr-Title/Comments via Cloud Website',
								'zAddAssetAttr-Accessibility Description',
								'zAddAssetAttr-Photo Stream Tag ID',
								'zAddAssetAttr-Share Type',
								'zAddAssetAttr-Library Scope Asset Contributors To Update',
								'zAsset-Overall Aesthetic Score',
								'zAsset-zENT',
								'zAsset-zOPT',
								'zAsset-Master= zCldMast-zPK',
								'zAsset-Extended Attributes= zExtAttr-zPK',
								'zAsset-Import Session Key',
								'zAsset-Photo Analysis Attributes Key',
								'zAsset-FOK-Cloud Feed Asset Entry Key',
								'zAsset-Computed Attributes Asset Key',
								'zAsset-Promotion Score',
								'zAsset-Media Analysis Attributes Key',
								'zAsset-Media Group UUID',
								'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
								'zAsset.Cloud Collection GUID',
								'zAddAssetAttr-zENT',
								'ZAddAssetAttr-zOPT',
								'zAddAssetAttr-zAsset= zAsset_zPK',
								'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
								'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
								'zAddAssetAttr-Public Global UUID',
								'zAddAssetAttr-Original Assets UUID',
								'zAddAssetAttr-Originating Asset Identifier',
								'zAddAssetAttr.Adjusted Fingerprint',
								'zCldMast-zPK= zAsset-Master',
								'zCldMast-zENT',
								'zCldMast-zOPT',
								'zCldMast-Moment Share Key= zShare-zPK',
								'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
								'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
								'zCldMast-Originating Asset ID',
								'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
								'CMzCldMastMedData-zENT',
								'CMzCldMastMedData-CldMast= zCldMast-zPK',
								'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
								'AAAzCldMastMedData-zENT',
								'AAAzCldMastMedData-CldMast key',
								'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
								'zExtAttr-zPK= zAsset-zExtendedAttributes',
								'zExtAttr-zENT',
								'zExtAttr-zOPT',
								'zExtAttr-Asset Key',
								'zIntResou-zPK',
								'zIntResou-zENT',
								'zIntResou-zOPT',
								'zIntResou-Asset= zAsset_zPK',
								'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
								'zMedAnlyAstAttr-zEnt',
								'zMedAnlyAstAttr-zOpt',
								'zMedAnlyAstAttr-Asset= zAsset-zPK')
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = 'Ph50.2-Asset_IntResou-SyndPL'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = 'Ph50.2-Asset_IntResou-SyndPL'
				timeline(report_folder, tlactivity, data_list, data_headers)

			else:
				logfunc('No Internal Resource data available for iOS 16 Syndication Photos Library Photos.sqlite')

			db.close()
			return

		elif version.parse(iosversion) >= version.parse("17"):
			file_found = str(files_found[0])
			db = open_sqlite_db_readonly(file_found)
			cursor = db.cursor()

			cursor.execute("""
			SELECT
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-4QueryStart',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability-4QueryStart',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability-4QueryStart',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type-4QueryStart',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type-4QueryStart',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID-4QueryStart',
			CASE zAsset.ZCOMPLETE
				WHEN 1 THEN '1-Yes-1'
			END AS 'zAsset Complete',
			zAsset.Z_PK AS 'zAsset-zPK',
			zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
			zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
			zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
			zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
			CASE zAsset.ZBUNDLESCOPE
				WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
				WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
				WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
				WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
			END AS 'zAsset-Bundle Scope',
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
			CASE zAsset.ZCLOUDISMYASSET
				WHEN 0 THEN '0-Not_My_Asset_in_Shared_Album-0'
				WHEN 1 THEN '1-My_Asset_in_Shared_Album-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISMYASSET || ''
			END AS 'zAsset-Cloud is My Asset',
			CASE zAsset.ZCLOUDISDELETABLE
				WHEN 0 THEN '0-No-0'
				WHEN 1 THEN '1-Yes-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDISDELETABLE || ''
			END AS 'zAsset-Cloud is deletable/Asset',
			CASE zAsset.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Album-Conv_or_iCldPhotos_OFF=Asset_Not_Synced-0'
				WHEN 1 THEN 'iCldPhotos ON=Asset_Can-Be-or-Has-Been_Synced_with_iCloud-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDLOCALSTATE || ''
			END AS 'zAsset-Cloud_Local_State',
			CASE zAsset.ZVISIBILITYSTATE
				WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
				WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
			END AS 'zAsset-Visibility State',
			zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
			zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
			zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
			CASE zExtAttr.ZFLASHFIRED
				WHEN 0 THEN '0-No Flash-0'
				WHEN 1 THEN '1-Flash Fired-1'
				ELSE 'Unknown-New-Value!: ' || zExtAttr.ZFLASHFIRED || ''
			END AS 'zExtAttr-Flash Fired',
			zExtAttr.ZFOCALLENGTH AS 'zExtAttr-Focal Lenght',
			zExtAttr.ZFOCALLENGTHIN35MM AS 'zExtAttr-Focal Lenth in 35MM',
			zExtAttr.ZDIGITALZOOMRATIO AS 'zExtAttr-Digital Zoom Ratio',
			CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
			END AS 'zAsset-Derived Camera Capture Device',
			CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
				WHEN 0 THEN '0-Back-Camera/Other-0'
				WHEN 1 THEN '1-Front-Camera-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
			END AS 'zAddAssetAttr-Camera Captured Device',
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
			zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
			zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
			zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
			zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
			zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
			zAsset.ZFILENAME AS 'zAsset-Filename',
			zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
			zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
			zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
			CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
				WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
				WHEN 1 THEN '1-Asset-In-Active-SPL-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
			END AS 'zAsset-Active Library Scope Participation State',
			CASE zAsset.ZLIBRARYSCOPESHARESTATE
				WHEN 0 THEN '0-Asset-Not-In-SPL-0'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
			END AS 'zAsset-Library Scope Share State- StillTesting',
			DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
			DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
			CASE zAddAssetAttr.ZDATECREATEDSOURCE
				WHEN 0 THEN '0-Cloud-Asset-0'
				WHEN 1 THEN '1-Local_Asset_EXIF-1'
				WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
			END AS 'zAddAssetAttr-Date Created Source',
			DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
			DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
			DateTime(zIntResou.ZCLOUDMASTERDATECREATED + 978307200, 'UNIXEPOCH') AS 'zIntResou-CldMst Date Created',
			zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
			zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
			zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
			zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
			DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
			DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
			DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
			CASE zCldMast.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-Not Synced with Cloud-0'
				WHEN 1 THEN '1-Pending Upload-1'
				WHEN 2 THEN '2-StillTesting'
				WHEN 3 THEN '3-Synced with Cloud-3'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
			END AS 'zCldMast-Cloud Local State',
			DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
			DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
			zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
			DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
			zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
			DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
			DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
			zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
			zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
			zAddAssetAttr.ZUPLOADATTEMPTS AS 'zAddAssetAttr-Upload Attempts',
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
			CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
				WHEN 0 THEN '0-Reverse Location Not Valid-0'
				WHEN 1 THEN '1-Reverse Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
			END AS 'zAddAssetAttr-Reverse Location Is Valid',
			CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
				WHEN 0 THEN '0-Shifted Location Not Valid-0'
				WHEN 1 THEN '1-Shifted Location Valid-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
			END AS 'zAddAssetAttr-Shifted Location Valid',
			CASE AAAzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Cloud-1'
				WHEN 2 THEN '2-StillTesting-This Device-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
			END AS 'AAAzCldMastMedData-zOPT',
			zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
			CASE CMzCldMastMedData.Z_OPT
				WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
				WHEN 2 THEN '2-StillTesting-Local_Asset-2'
				WHEN 3 THEN '3-StillTesting-Muted-3'
				WHEN 4 THEN '4-StillTesting-Unknown-4'
				WHEN 5 THEN '5-StillTesting-Unknown-5'
				ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
			END AS 'CldMasterzCldMastMedData-zOPT',
			zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
			CASE zAsset.ZSEARCHINDEXREBUILDSTATE
				WHEN 0 THEN '0-StillTesting-0'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZSEARCHINDEXREBUILDSTATE || ''
			END AS 'zAsset-Search Index Rebuild State',
			zAddAssetAttr.ZSYNDICATIONHISTORY AS 'zAddAssetAttr-Syndication History',
			zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVERSION AS 'zMedAnlyAstAttr-Syndication Processing Version',
			CASE zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-STILLTESTING_Wide-Camera_JPG-1'
				WHEN 2 THEN '2-STILLTESTING_Telephoto_Camear_Lens-2'
				WHEN 4 THEN '4-STILLTESTING_SWY_Asset_OrigAssetImport_SystemPackageApp-4'
				WHEN 16 THEN '16-STILLTESTING-16'
				WHEN 1024 THEN '1024-STILLTESTING_SWY_Asset_OrigAssetImport_NativeCamera-1024'
				WHEN 2048 THEN '2048-STILLTESTING-2048'
				WHEN 4096 THEN '4096-STILLTESTING_SWY_Asset_Manually_Saved-4096'
				ELSE 'Unknown-New-Value!: ' || zMedAnlyAstAttr.ZSYNDICATIONPROCESSINGVALUE || ''
			END AS 'zMedAnlyAstAttr-Syndication Processing Value',
			CASE zAsset.ZORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAsset-Orientation',
			CASE zAddAssetAttr.ZORIGINALORIENTATION
				WHEN 1 THEN '1-Video-Default/Adjustment/Horizontal-Camera-(left)-1'
				WHEN 2 THEN '2-Horizontal-Camera-(right)-2'
				WHEN 3 THEN '3-Horizontal-Camera-(right)-3'
				WHEN 4 THEN '4-Horizontal-Camera-(left)-4'
				WHEN 5 THEN '5-Vertical-Camera-(top)-5'
				WHEN 6 THEN '6-Vertical-Camera-(top)-6'
				WHEN 7 THEN '7-Vertical-Camera-(bottom)-7'
				WHEN 8 THEN '8-Vertical-Camera-(bottom)-8'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZORIENTATION || ''
			END AS 'zAddAssetAttr-Original Orientation',
			CASE zAsset.ZKIND
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
			END AS 'zAsset-Kind',
			CASE zAsset.ZKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-Paorama-1'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
			END AS 'zAsset-Kind-Sub-Type',
			CASE zAddAssetAttr.ZCLOUDKINDSUBTYPE
				WHEN 0 THEN '0-Still-Photo-0'
				WHEN 1 THEN '1-StillTesting'
				WHEN 2 THEN '2-Live-Photo-2'
				WHEN 3 THEN '3-Screenshot-3'
				WHEN 10 THEN '10-SpringBoard-Screenshot-10'
				WHEN 100 THEN '100-Video-100'
				WHEN 101 THEN '101-Slow-Mo-Video-101'
				WHEN 102 THEN '102-Time-lapse-Video-102'
				WHEN 103 THEN '103-Replay_Screen_Recording-103'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDKINDSUBTYPE || ''
			END AS 'zAddAssetAttr-Cloud Kind Sub Type',
			CASE zAsset.ZPLAYBACKSTYLE
				WHEN 1 THEN '1-Image-1'
				WHEN 2 THEN '2-Image-Animated-2'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 4 THEN '4-Video-4'
				WHEN 5 THEN '5-Video-Looping-5'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKSTYLE || ''
			END AS 'zAsset-Playback Style',
			CASE zAsset.ZPLAYBACKVARIATION
				WHEN 0 THEN '0-No_Playback_Variation-0'
				WHEN 1 THEN '1-StillTesting_Playback_Variation-1'
				WHEN 2 THEN '2-StillTesting_Playback_Variation-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZPLAYBACKVARIATION || ''
			END AS 'zAsset-Playback Variation',
			zAsset.ZDURATION AS 'zAsset-Video Duration',
			zExtAttr.ZDURATION AS 'zExtAttr-Duration',
			zAsset.ZVIDEOCPDURATIONVALUE AS 'zAsset-Video CP Duration',
			zAddAssetAttr.ZVIDEOCPDURATIONTIMESCALE AS 'zAddAssetAttr-Video CP Duration Time Scale',
			zAsset.ZVIDEOCPVISIBILITYSTATE AS 'zAsset-Video CP Visibility State',
			zAddAssetAttr.ZVIDEOCPDISPLAYVALUE AS 'zAddAssetAttr-Video CP Display Value',
			zAddAssetAttr.ZVIDEOCPDISPLAYTIMESCALE AS 'zAddAssetAttr-Video CP Display Time Scale',
			CASE zIntResou.ZDATASTORECLASSID
				WHEN 0 THEN '0-LPL-Asset_CPL-Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-Photo-Cloud-Sharing-Asset-2'
				WHEN 3 THEN '3-SWY_Syndication_Asset-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORECLASSID || ''
			END AS 'zIntResou-Datastore Class ID',
			CASE zAsset.ZCLOUDPLACEHOLDERKIND
				WHEN 0 THEN '0-Local&CloudMaster Asset-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-StillTesting-2'
				WHEN 3 THEN '3-JPG-Asset_Only_PhDa/Thumb/V2-3'
				WHEN 4 THEN '4-LPL-JPG-Asset_CPLAsset-OtherType-4'
				WHEN 5 THEN '5-Asset_synced_CPL_2_Device-5'
				WHEN 6 THEN '6-StillTesting-6'
				WHEN 7 THEN '7-LPL-poster-JPG-Asset_CPLAsset-MP4-7'
				WHEN 8 THEN '8-LPL-JPG_Asset_CPLAsset-LivePhoto-MOV-8'
				WHEN 9 THEN '9-CPL_MP4_Asset_Saved_2_LPL-9'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDPLACEHOLDERKIND || ''
			END AS 'zAsset-Cloud Placeholder Kind',
			CASE zIntResou.ZLOCALAVAILABILITY
				WHEN -1 THEN '(-1)-IR_Asset_Not_Avail_Locally(-1)'
				WHEN 1 THEN '1-IR_Asset_Avail_Locally-1'
				WHEN -32768 THEN '(-32768)_IR_Asset-SWY-Linked_Asset(-32768)'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITY || ''
			END AS 'zIntResou-Local Availability',
			CASE zIntResou.ZLOCALAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZLOCALAVAILABILITYTARGET || ''
			END AS 'zIntResou-Local Availability Target',
			CASE zIntResou.ZCLOUDLOCALSTATE
				WHEN 0 THEN '0-IR_Asset_Not_Synced_No_IR-CldMastDateCreated-0'
				WHEN 1 THEN '1-IR_Asset_Pening-Upload-1'
				WHEN 2 THEN '2-IR_Asset_Photo_Cloud_Share_Asset_On-Local-Device-2'
				WHEN 3 THEN '3-IR_Asset_Synced_iCloud-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDLOCALSTATE || ''
			END AS 'zIntResou-Cloud Local State',
			CASE zIntResou.ZREMOTEAVAILABILITY
				WHEN 0 THEN '0-IR_Asset-Not-Avail-Remotely-0'
				WHEN 1 THEN '1-IR_Asset_Avail-Remotely-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITY || ''
			END AS 'zIntResou-Remote Availability',
			CASE zIntResou.ZREMOTEAVAILABILITYTARGET
				WHEN 0 THEN '0-StillTesting-0'
				WHEN 1 THEN '1-StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZREMOTEAVAILABILITYTARGET || ''
			END AS 'zIntResou-Remote Availability Target',
			zIntResou.ZTRANSIENTCLOUDMASTER AS 'zIntResou-Transient Cloud Master',
			zIntResou.ZSIDECARINDEX AS 'zIntResou-Side Car Index',
			zIntResou.ZFILEID AS 'zIntResou- File ID',
			CASE zIntResou.ZVERSION
				WHEN 0 THEN '0-IR_Asset_Standard-0'
				WHEN 1 THEN '1-StillTesting-1'
				WHEN 2 THEN '2-IR_Asset_Adjustments-Mutation-2'
				WHEN 3 THEN '3-IR_Asset_No_IR-CldMastDateCreated-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZVERSION || ''
			END AS 'zIntResou-Version',
			zAddAssetAttr.ZORIGINALFILESIZE AS 'zAddAssetAttr- Original-File-Size',
			CASE zIntResou.ZRESOURCETYPE
				WHEN 0 THEN '0-Photo-0'
				WHEN 1 THEN '1-Video-1'
				WHEN 3 THEN '3-Live-Photo-3'
				WHEN 5 THEN '5-Adjustement-Data-5'
				WHEN 6 THEN '6-Screenshot-6'
				WHEN 9 THEN '9-AlternatePhoto-3rdPartyApp-StillTesting-9'
				WHEN 13 THEN '13-Movie-13'
				WHEN 14 THEN '14-Wallpaper-14'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRESOURCETYPE || ''
			END AS 'zIntResou-Resource Type',
			CASE zIntResou.ZDATASTORESUBTYPE
				WHEN 0 THEN '0-No Cloud Inter Resource-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZDATASTORESUBTYPE || ''
			END AS 'zIntResou-Datastore Sub-Type',
			CASE zIntResou.ZCLOUDSOURCETYPE
				WHEN 0 THEN '0-NA-0'
				WHEN 1 THEN '1-Main-Asset-Orig-Size-1'
				WHEN 2 THEN '2-Photo-with-Adjustments-2'
				WHEN 3 THEN '3-JPG-Large-Thumb-3'
				WHEN 4 THEN '4-JPG-Med-Thumb-4'
				WHEN 5 THEN '5-JPG-Small-Thumb-5'
				WHEN 6 THEN '6-Video-Med-Data-6'
				WHEN 7 THEN '7-Video-Small-Data-7'
				WHEN 8 THEN '8-MP4-Cloud-Share-8'
				WHEN 9 THEN '9-StillTesting'
				WHEN 10 THEN '10-3rdPartyApp_thumb-StillTesting-10'
				WHEN 11 THEN '11-StillTesting'
				WHEN 12 THEN '12-StillTesting'
				WHEN 13 THEN '13-PNG-Optimized_CPLAsset-13'
				WHEN 14 THEN '14-Wallpaper-14'
				WHEN 15 THEN '15-Has-Markup-and-Adjustments-15'
				WHEN 16 THEN '16-Video-with-Adjustments-16'
				WHEN 17 THEN '17-RAW_Photo-17_RT'
				WHEN 18 THEN '18-Live-Photo-Video_Optimized_CPLAsset-18'
				WHEN 19 THEN '19-Live-Photo-with-Adjustments-19'
				WHEN 20 THEN '20-StillTesting'
				WHEN 21 THEN '21-MOV-Optimized_HEVC-4K_video-21'
				WHEN 22 THEN '22-Adjust-Mutation_AAE_Asset-22'
				WHEN 23 THEN '23-StillTesting'
				WHEN 24 THEN '24-StillTesting'
				WHEN 25 THEN '25-StillTesting'
				WHEN 26 THEN '26-MOV-Optimized_CPLAsset-26'
				WHEN 27 THEN '27-StillTesting'
				WHEN 28 THEN '28-MOV-Med-hdr-Data-28'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDSOURCETYPE || ''
			END AS 'zIntResou-Cloud Source Type',
			zIntResou.ZDATALENGTH AS 'zIntResou-Data Length',
			CASE zIntResou.ZRECIPEID
				WHEN 0 THEN '0-OrigFileSize_match_DataLength_or_Optimized-0'
				WHEN 65737 THEN '65737-full-JPG_Orig-ProRAW_DNG-65737'
				WHEN 65739 THEN '65739-JPG_Large_Thumb-65739'
				WHEN 65741 THEN '65741-Various_Asset_Types-or-Thumbs-65741'
				WHEN 65743 THEN '65743-ResouType-Photo_5003-or-5005-JPG_Thumb-65743'
				WHEN 65749 THEN '65749-LocalVideoKeyFrame-JPG_Thumb-65749'
				WHEN 65938 THEN '65938-FullSizeRender-Photo-or-plist-65938'
				WHEN 131072 THEN '131072-FullSizeRender-Video-or-plist-131072'
				WHEN 131077 THEN '131077-medium-MOV_HEVC-4K-131077'
				WHEN 131079 THEN '131079-medium-MP4_Adj-Mutation_Asset-131079'
				WHEN 131081 THEN '131081-ResouType-Video_5003-or-5005-JPG_Thumb-131081'
				WHEN 131272 THEN '131272-FullSizeRender-Video_LivePhoto_Adj-Mutation-131272'
				WHEN 131275 THEN '131275-medium-MOV_LivePhoto-131275'
				WHEN 131277 THEN '131277-No-IR-Asset_LivePhoto-iCloud_Sync_Asset-131277'
				WHEN 131475 THEN '131475-medium-hdr-MOV-131475'
				WHEN 327683 THEN '327683-JPG-Thumb_for_3rdParty-StillTesting-327683'
				WHEN 327687 THEN '627687-WallpaperComputeResource-627687'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZRECIPEID || ''
			END AS 'zIntResou-Recipe ID',
			CASE zIntResou.ZCLOUDLASTPREFETCHDATE
				WHEN 0 THEN '0-NA-0'
				ELSE DateTime(zIntResou.ZCLOUDLASTPREFETCHDATE + 978307200, 'UNIXEPOCH')
			END AS 'zIntResou-Cloud Last Prefetch Date',
			zIntResou.ZCLOUDPREFETCHCOUNT AS 'zIntResou-Cloud Prefetch Count',
			DateTime(zIntResou.ZCLOUDLASTONDEMANDDOWNLOADDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou- Cloud-Last-OnDemand Download-Date',
			CASE zIntResou.ZUTICONFORMANCEHINT
				WHEN 0 THEN '0-NA/Doesnt_Conform-0'
				WHEN 1 THEN '1-UTTypeImage-1'
				WHEN 2 THEN '2-UTTypeProRawPhoto-2'
				WHEN 3 THEN '3-UTTypeMovie-3'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
			END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
			CASE zIntResou.ZCOMPACTUTI
				WHEN 1 THEN '1-JPEG/THM-1'
				WHEN 3 THEN '3-HEIC-3'
				WHEN 6 THEN '6-PNG-6'
				WHEN 7 THEN '7-StillTesting'
				WHEN 9 THEN '9-DNG-9'
				WHEN 23 THEN '23-JPEG/HEIC/quicktime-mov-23'
				WHEN 24 THEN '24-MPEG4-24'
				WHEN 36 THEN '36-Wallpaper-36'
				WHEN 37 THEN '37-Adj/Mutation_Data-37'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCOMPACTUTI || ''
			END AS 'zIntResou-Compact-UTI',
			zAsset.ZUNIFORMTYPEIDENTIFIER AS 'zAsset-Uniform Type ID',
			zAsset.ZORIGINALCOLORSPACE AS 'zAsset-Original Color Space',
			zCldMast.ZUNIFORMTYPEIDENTIFIER AS 'zCldMast-Uniform_Type_ID',
			CASE zCldMast.ZFULLSIZEJPEGSOURCE
				WHEN 0 THEN '0-CldMast-JPEG-Source-Video Still-Testing-0'
				WHEN 1 THEN '1-CldMast-JPEG-Source-Other- Still-Testing-1'
				ELSE 'Unknown-New-Value!: ' || zCldMast.ZFULLSIZEJPEGSOURCE || ''
			END AS 'zCldMast-Full Size JPEG Source',
			zAsset.ZHDRGAIN AS 'zAsset-HDR Gain',
			CASE zAsset.ZHDRTYPE
				WHEN 0 THEN '0-No-HDR-0'
				WHEN 3 THEN '3-HDR_Photo-3_RT'
				WHEN 4 THEN '4-Non-HDR_Version-4_RT'
				WHEN 5 THEN '5-HEVC_Movie-5'
				WHEN 6 THEN '6-Panorama-6_RT'
				WHEN 10 THEN '10-HDR-Gain-10'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHDRTYPE || ''
			END AS 'zAsset-zHDR_Type',
			zExtAttr.ZCODEC AS 'zExtAttr-Codec',
			zIntResou.ZCODECFOURCHARCODENAME AS 'zIntResou-Codec Four Char Code Name',
			zCldMast.ZCODECNAME AS 'zCldMast-Codec Name',
			zCldMast.ZVIDEOFRAMERATE AS 'zCldMast-Video Frame Rate',
			zCldMast.ZPLACEHOLDERSTATE AS 'zCldMast-Placeholder State',
			CASE zAsset.ZDEPTHTYPE
				WHEN 0 THEN '0-Not_Portrait-0_RT'
				ELSE 'Portrait: ' || zAsset.ZDEPTHTYPE || ''
			END AS 'zAsset-Depth_Type',
			zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
			CASE zAsset.ZAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
			END AS 'zAsset-Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
				WHEN 0 THEN '0-NA/Single_Asset_Burst_UUID-0_RT'
				WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
				WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
				WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
				WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
				WHEN 32 THEN '32-StillTesting-32_RT'
				WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
			END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
			CASE zAddAssetAttr.ZCLOUDRECOVERYSTATE
				WHEN 0 THEN '0-StillTesting'
				WHEN 1 THEN '1-StillTesting'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDRECOVERYSTATE || ''
			END AS 'zAddAssetAttr-Cloud Recovery State',
			zAddAssetAttr.ZCLOUDSTATERECOVERYATTEMPTSCOUNT AS 'zAddAssetAttr-Cloud State Recovery Attempts Count',
			zAsset.ZDEFERREDPROCESSINGNEEDED AS 'zAsset-Deferred Processing Needed',
			zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
			zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
			zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
			CASE zAsset.ZHASADJUSTMENTS
				WHEN 0 THEN '0-No-Adjustments-0'
				WHEN 1 THEN '1-Yes-Adjustments-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
			END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',
			DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
			zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
			zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
			CASE zAsset.ZFAVORITE
				WHEN 0 THEN '0-Asset Not Favorite-0'
				WHEN 1 THEN '1-Asset Favorite-1'
			END AS 'zAsset-Favorite',
			CASE zAsset.ZHIDDEN
				WHEN 0 THEN '0-Asset Not Hidden-0'
				WHEN 1 THEN '1-Asset Hidden-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
			END AS 'zAsset-Hidden',
			CASE zAsset.ZTRASHEDSTATE
				WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
			END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
			DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
			zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
			CASE zAsset.ZDELETEREASON
				WHEN 1 THEN '1-StillTesting Delete-Reason-1'
				WHEN 2 THEN '2-StillTesting Delete-Reason-2'
				WHEN 3 THEN '3-StillTesting Delete-Reason-3'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
			END AS 'zAsset-Delete-Reason',
			CASE zIntResou.ZTRASHEDSTATE
				WHEN 0 THEN '0-zIntResou-Not In Trash/Recently Deleted-0'
				WHEN 1 THEN '1-zIntResou-In Trash/Recently Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZTRASHEDSTATE || ''
			END AS 'zIntResou-Trash State',
			DateTime(zIntResou.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zIntResou-Trashed Date',
			CASE zAsset.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud Asset Not Deleted-0'
				WHEN 1 THEN '1-Cloud Asset Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDDELETESTATE || ''
			END AS 'zAsset-Cloud Delete State',
			CASE zIntResou.ZCLOUDDELETESTATE
				WHEN 0 THEN '0-Cloud IntResou Not Deleted-0'
				WHEN 1 THEN '1-Cloud IntResou Deleted-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZCLOUDDELETESTATE || ''
			END AS 'zIntResou-Cloud Delete State',
			CASE zAddAssetAttr.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP Not in Trash-0'
				WHEN 1 THEN '1-PTP In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZPTPTRASHEDSTATE || ''
			END AS 'zAddAssetAttr-PTP Trashed State',
			CASE zIntResou.ZPTPTRASHEDSTATE
				WHEN 0 THEN '0-PTP IntResou Not in Trash-0'
				WHEN 1 THEN '1-PTP IntResou In Trash-1'
				ELSE 'Unknown-New-Value!: ' || zIntResou.ZPTPTRASHEDSTATE || ''
			END AS 'zIntResou-PTP Trashed State',
			zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
			DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
			DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',
			zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
			zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
			zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
			zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
			zAddAssetAttr.ZPENDINGSHARECOUNT AS 'zAddAssetAttr- Pending Share Count',
			zAddAssetAttr.ZSHARECOUNT AS 'zAddAssetAttr- Share Count',
			CASE zAddAssetAttr.ZALLOWEDFORANALYSIS
				WHEN 0 THEN '0-Asset Not Allowed For Analysis-0'
				WHEN 1 THEN '1-Asset Allowed for Analysis-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZALLOWEDFORANALYSIS || ''
			END AS 'zAddAssetAttr-Allowed for Analysis',
			zAddAssetAttr.ZSCENEANALYSISVERSION AS 'zAddAssetAttr-Scene Analysis Version',
			CASE zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW
				WHEN 0 THEN '0-No-0'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSCENEANALYSISISFROMPREVIEW || ''
			END AS 'zAddAssetAttr-Scene Analysis is From Preview',
			DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
			CASE zAsset.ZDUPLICATEASSETVISIBILITYSTATE
				WHEN 0 THEN '0-No-Duplicates-0'
				WHEN 1 THEN '1-Has Duplicate-1'
				WHEN 2 THEN '2-Is a Duplicate-2'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZDUPLICATEASSETVISIBILITYSTATE || ''
			END AS 'zAsset-Duplication Asset Visibility State',
			CASE zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE
				WHEN 0 THEN '0-No Copy-0'
				WHEN 1 THEN '1-Has A Copy-1'
				WHEN 2 THEN '2-Has A Copy-2'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDESTINATIONASSETCOPYSTATE || ''
			END AS 'zAddAssetAttr-Destination Asset Copy State',
			CASE zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE
				WHEN 0 THEN '0-Unknown-StillTesting-0'
				WHEN 1 THEN '1-Unknown-StillTesting-1'
				WHEN 2 THEN '2-Unknown-StillTesting-2'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDUPLICATEDETECTORPERCEPTUALPROCESSINGSTATE || ''
			END AS 'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
			zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONSCOPEIDENTIFIER AS 'zAddAssetAttr-Source Asset for Duplication Scope ID',
			zCldMast.ZSOURCEMASTERFORDUPLICATIONSCOPEIDENTIFIER AS 'zCldMast-Source Master For Duplication Scope ID',
			zAddAssetAttr.ZSOURCEASSETFORDUPLICATIONIDENTIFIER AS 'zAddAssetAttr-Source Asset For Duplication ID',
			zCldMast.ZSOURCEMASTERFORDUPLICATIONIDENTIFIER AS 'zCldMast-Source Master for Duplication ID',
			zAddAssetAttr.ZVARIATIONSUGGESTIONSTATES AS 'zAddAssetAttr-Variation Suggestions States',
			zAsset.ZHIGHFRAMERATESTATE AS 'zAsset-High Frame Rate State',
			zAsset.ZVIDEOKEYFRAMETIMESCALE AS 'zAsset-Video Key Frame Time Scale',
			zAsset.ZVIDEOKEYFRAMEVALUE AS 'zAsset-Video Key Frame Value',
			zExtAttr.ZISO AS 'zExtAttr-ISO',
			zExtAttr.ZMETERINGMODE AS 'zExtAttr-Metering Mode',
			zExtAttr.ZSAMPLERATE AS 'zExtAttr-Sample Rate',
			zExtAttr.ZTRACKFORMAT AS 'zExtAttr-Track Format',
			zExtAttr.ZWHITEBALANCE AS 'zExtAttr-White Balance',
			zExtAttr.ZAPERTURE AS 'zExtAttr-Aperture',
			zExtAttr.ZBITRATE AS 'zExtAttr-BitRate',
			zExtAttr.ZEXPOSUREBIAS AS 'zExtAttr-Exposure Bias',
			zExtAttr.ZFPS AS 'zExtAttr-Frames Per Second',
			zExtAttr.ZSHUTTERSPEED AS 'zExtAttr-Shutter Speed',
			zExtAttr.ZSLUSHSCENEBIAS AS 'zExtAttr-Slush Scene Bias',
			zExtAttr.ZSLUSHVERSION AS 'zExtAttr-Slush Version',
			zExtAttr.ZSLUSHPRESET AS 'zExtAttr-Slush Preset',
			zExtAttr.ZSLUSHWARMTHBIAS AS 'zExtAttr-Slush Warm Bias',
			zAsset.ZHEIGHT AS 'zAsset-Height',
			zAddAssetAttr.ZORIGINALHEIGHT AS 'zAddAssetAttr-Original Height',
			zIntResou.ZUNORIENTEDHEIGHT AS 'zIntResou-Unoriented Height',
			zAsset.ZWIDTH AS 'zAsset-Width',
			zAddAssetAttr.ZORIGINALWIDTH AS 'zAddAssetAttr-Original Width',
			zIntResou.ZUNORIENTEDWIDTH AS 'zIntResou-Unoriented Width',
			zAsset.ZTHUMBNAILINDEX AS 'zAsset-Thumbnail Index',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILHEIGHT AS 'zAddAssetAttr-Embedded Thumbnail Height',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILLENGTH AS 'zAddAssetAttr-Embedded Thumbnail Length',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILOFFSET AS 'zAddAssetAttr-Embedded Thumbnail Offset',
			zAddAssetAttr.ZEMBEDDEDTHUMBNAILWIDTH AS 'zAddAssetAttr-Embedded Thumbnail Width',
			zAsset.ZPACKEDACCEPTABLECROPRECT AS 'zAsset-Packed Acceptable Crop Rect',
			zAsset.ZPACKEDBADGEATTRIBUTES AS 'zAsset-Packed Badge Attributes',
			zAsset.ZPACKEDPREFERREDCROPRECT AS 'zAsset-Packed Preferred Crop Rect',
			zAsset.ZCURATIONSCORE AS 'zAsset-Curation Score',
			zAsset.ZCAMERAPROCESSINGADJUSTMENTSTATE AS 'zAsset-Camera Processing Adjustment State',
			zAsset.ZDEPTHTYPE AS 'zAsset-Depth Type',
			zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',		
			CASE zAddAssetAttr.ZORIGINALRESOURCECHOICE
				WHEN 0 THEN '0-JPEG Original Resource-0'
				WHEN 1 THEN '1-RAW Original Resource-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZORIGINALRESOURCECHOICE || ''
			END AS 'zAddAssetAttr-Orig Resource Choice',
			CASE zAsset.ZSPATIALTYPE
				WHEN 0 THEN '0-UnknownTesting-0'
				ELSE 'Unknown-New-Value!: ' || zAsset.ZSPATIALTYPE || ''
			END AS 'zAsset-Spatial Type',
			zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
			zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
			zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity-HEX',
			zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
			zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title/Comments via Cloud Website',
			zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
			zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
			CASE zAddAssetAttr.ZSHARETYPE
				WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
				WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
				ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
			END AS 'zAddAssetAttr-Share Type',
			zAddAssetAttr.ZLIBRARYSCOPEASSETCONTRIBUTORSTOUPDATE AS 'zAddAssetAttr-Library Scope Asset Contributors To Update',
			zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',		
			zAsset.Z_ENT AS 'zAsset-zENT',
			zAsset.Z_OPT AS 'zAsset-zOPT',
			zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
			zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
			zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
			zAsset.ZPHOTOANALYSISATTRIBUTES AS 'zAsset-Photo Analysis Attributes Key',
			zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
			zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
			zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
			zAsset.ZICONICSCORE AS 'zAsset-Iconic Score',
			zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
			zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
			zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
			zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
			zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
			zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
			zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
			zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
			zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
			zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
			zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
			zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
			zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',		
			zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
			zCldMast.Z_ENT AS 'zCldMast-zENT',
			zCldMast.Z_OPT AS 'zCldMast-zOPT',
			zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
			zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
			zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
			zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
			CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
			CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
			CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
			AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
			AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
			AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
			AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
			zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
			zExtAttr.Z_ENT AS 'zExtAttr-zENT',
			zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
			zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
			zIntResou.Z_PK AS 'zIntResou-zPK',
			zIntResou.Z_ENT AS 'zIntResou-zENT',
			zIntResou.Z_OPT AS 'zIntResou-zOPT',
			zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
			zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
			zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
			zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
			zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK'
			FROM ZASSET zAsset
				LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
				LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
				LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
				LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT		
				LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
				LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
				LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
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
									  row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
									  row[91], row[92], row[93], row[94], row[95], row[96], row[97], row[98], row[99],
									  row[100], row[101], row[102], row[103], row[104], row[105], row[106], row[107],
									  row[108], row[109], row[110], row[111], row[112], row[113], row[114], row[115],
									  row[116], row[117], row[118], row[119], row[120], row[121], row[122], row[123],
									  row[124], row[125], row[126], row[127], row[128], row[129], row[130], row[131],
									  row[132], row[133], row[134], row[135], row[136], row[137], row[138], row[139],
									  row[140], row[141], row[142], row[143], row[144], row[145], row[146], row[147],
									  row[148], row[149], row[150], row[151], row[152], row[153], row[154], row[155],
									  row[156], row[157], row[158], row[159], row[160], row[161], row[162], row[163],
									  row[164], row[165], row[166], row[167], row[168], row[169], row[170], row[171],
									  row[172], row[173], row[174], row[175], row[176], row[177], row[178], row[179],
									  row[180], row[181], row[182], row[183], row[184], row[185], row[186], row[187],
									  row[188], row[189], row[190], row[191], row[192], row[193], row[194], row[195],
									  row[196], row[197], row[198], row[199], row[200], row[201], row[202], row[203],
									  row[204], row[205], row[206], row[207], row[208], row[209], row[210], row[211],
									  row[212], row[213], row[214], row[215], row[216], row[217], row[218], row[219],
									  row[220], row[221], row[222], row[223], row[224], row[225], row[226], row[227],
									  row[228], row[229], row[230], row[231], row[232], row[233], row[234], row[235],
									  row[236], row[237], row[238], row[239], row[240], row[241], row[242], row[243],
									  row[244], row[245], row[246], row[247], row[248], row[249], row[250], row[251],
									  row[252], row[253], row[254], row[255], row[256], row[257], row[258], row[259],
									  row[260], row[261], row[262], row[263], row[264], row[265], row[266], row[267],
									  row[268], row[269]))

					counter += 1

				description = 'Parses iOS 17 asset records from Syndication.photos.library/database/Photos.sqlite ZINTERNALRESOURCE and' \
							  ' and other tables. This and other related parsers should provide data for investigative' \
							  ' analysis of assets being stored locally on the device verses assets being stored in' \
							  ' iCloud Photos as the result of optimization. This is very large query and script,' \
							  ' I recommend opening the TSV generated report with Zimmermans Tools' \
							  ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
							  ' and filter the results.'
				report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
				report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
				report.add_script()
				data_headers = ('zAsset-Date Created-4QueryStart',
								'zIntResou-Local Availability-4QueryStart',
								'zIntResou-Remote Availability-4QueryStart',
								'zIntResou-Resource Type-4QueryStart',
								'zIntResou-Datastore Sub-Type-4QueryStart',
								'zIntResou-Recipe ID-4QueryStart',
								'zAsset Complete',
								'zAsset-zPK',
								'zAddAssetAttr-zPK',
								'zAsset-UUID = store.cloudphotodb',
								'zAddAssetAttr-Master Fingerprint',
								'zIntResou-Fingerprint',
								'zAsset-Bundle Scope',
								'zAsset-Syndication State',
								'zAsset-Cloud is My Asset',
								'zAsset-Cloud is deletable/Asset',
								'zAsset-Cloud_Local_State',
								'zAsset-Visibility State',
								'zExtAttr-Camera Make',
								'zExtAttr-Camera Model',
								'zExtAttr-Lens Model',
								'zExtAttr-Flash Fired',
								'zExtAttr-Focal Lenght',
								'zExtAttr-Focal Lenth in 35MM',
								'zExtAttr-Digital Zoom Ratio',
								'zAsset-Derived Camera Capture Device',
								'zAddAssetAttr-Camera Captured Device',
								'zAddAssetAttr-Imported by',
								'zCldMast-Imported By',
								'zAddAssetAttr.Imported by Bundle Identifier',
								'zAddAssetAttr-Imported By Display Name',
								'zCldMast-Imported by Bundle ID',
								'zCldMast-Imported by Display Name',
								'zAsset-Saved Asset Type',
								'zAsset-Directory/Path',
								'zAsset-Filename',
								'zAddAssetAttr- Original Filename',
								'zCldMast- Original Filename',
								'zAddAssetAttr- Syndication Identifier-SWY-Files',
								'zAsset-Active Library Scope Participation State',
								'zAsset-Library Scope Share State- StillTesting',
								'zAsset-Added Date',
								'zAsset- SortToken -CameraRoll',
								'zAddAssetAttr-Date Created Source',
								'zAsset-Date Created',
								'zCldMast-Creation Date',
								'zIntResou-CldMst Date Created',
								'zAddAssetAttr-Time Zone Name',
								'zAddAssetAttr-Time Zone Offset',
								'zAddAssetAttr-Inferred Time Zone Offset',
								'zAddAssetAttr-EXIF-String',
								'zAsset-Modification Date',
								'zAddAssetAttr-Last Viewed Date',
								'zAsset-Last Shared Date',
								'zCldMast-Cloud Local State',
								'zCldMast-Import Date',
								'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
								'zAddAssetAttr-Import Session ID',
								'zAddAssetAttr-Alt Import Image Date',
								'zCldMast-Import Session ID- AirDrop-StillTesting',
								'zAsset-Cloud Batch Publish Date',
								'zAsset-Cloud Server Publish Date',
								'zAsset-Cloud Download Requests',
								'zAsset-Cloud Batch ID',
								'zAddAssetAttr-Upload Attempts',
								'zAsset-Latitude',
								'zExtAttr-Latitude',
								'zAsset-Longitude',
								'zExtAttr-Longitude',
								'zAddAssetAttr-GPS Horizontal Accuracy',
								'zAddAssetAttr-Location Hash',
								'zAddAssetAttr-Reverse Location Is Valid',
								'zAddAssetAttr-Shifted Location Valid',
								'AAAzCldMastMedData-zOPT',
								'zAddAssetAttr-Media Metadata Type',
								'CldMasterzCldMastMedData-zOPT',
								'zCldMast-Media Metadata Type',
								'zAsset-Search Index Rebuild State',
								'zAddAssetAttr-Syndication History',
								'zMedAnlyAstAttr-Syndication Processing Version',
								'zMedAnlyAstAttr-Syndication Processing Value',
								'zAsset-Orientation',
								'zAddAssetAttr-Original Orientation',
								'zAsset-Kind',
								'zAsset-Kind-Sub-Type',
								'zAddAssetAttr-Cloud Kind Sub Type',
								'zAsset-Playback Style',
								'zAsset-Playback Variation',
								'zAsset-Video Duration',
								'zExtAttr-Duration',
								'zAsset-Video CP Duration',
								'zAddAssetAttr-Video CP Duration Time Scale',
								'zAsset-Video CP Visibility State',
								'zAddAssetAttr-Video CP Display Value',
								'zAddAssetAttr-Video CP Display Time Scale',
								'zIntResou-Datastore Class ID',
								'zAsset-Cloud Placeholder Kind',
								'zIntResou-Local Availability',
								'zIntResou-Local Availability Target',
								'zIntResou-Cloud Local State',
								'zIntResou-Remote Availability',
								'zIntResou-Remote Availability Target',
								'zIntResou-Transient Cloud Master',
								'zIntResou-Side Car Index',
								'zIntResou- File ID',
								'zIntResou-Version',
								'zAddAssetAttr- Original-File-Size',
								'zIntResou-Resource Type',
								'zIntResou-Datastore Sub-Type',
								'zIntResou-Cloud Source Type',
								'zIntResou-Data Length',
								'zIntResou-Recipe ID',
								'zIntResou-Cloud Last Prefetch Date',
								'zIntResou-Cloud Prefetch Count',
								'zIntResou- Cloud-Last-OnDemand Download-Date',
								'zIntResou-UniformTypeID_UTI_Conformance_Hint',
								'zIntResou-Compact-UTI',
								'zAsset-Uniform Type ID',
								'zAsset-Original Color Space',
								'zCldMast-Uniform_Type_ID',
								'zCldMast-Full Size JPEG Source',
								'zAsset-HDR Gain',
								'zAsset-zHDR_Type',
								'zExtAttr-Codec',
								'zIntResou-Codec Four Char Code Name',
								'zCldMast-Codec Name',
								'zCldMast-Video Frame Rate',
								'zCldMast-Placeholder State',
								'zAsset-Depth_Type',
								'zAsset-Avalanche UUID',
								'zAsset-Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud_Avalanche_Pick_Type/BurstAsset',
								'zAddAssetAttr-Cloud Recovery State',
								'zAddAssetAttr-Cloud State Recovery Attempts Count',
								'zAsset-Deferred Processing Needed',
								'zAsset-Video Deferred Processing Needed',
								'zAddAssetAttr-Deferred Photo Identifier',
								'zAddAssetAttr-Deferred Processing Candidate Options',
								'zAsset-Has Adjustments/Camera-Effects-Filters',
								'zAsset-Adjustment Timestamp',
								'zAddAssetAttr-Editor Bundle ID',
								'zAddAssetAttr-Montage',
								'zAsset-Favorite',
								'zAsset-Hidden',
								'zAsset-Trashed State/LocalAssetRecentlyDeleted',
								'zAsset-Trashed Date',
								'zAsset-Trashed by Participant= zSharePartic_zPK',
								'zAsset-Delete-Reason',
								'zIntResou-Trash State',
								'zIntResou-Trashed Date',
								'zAsset-Cloud Delete State',
								'zIntResou-Cloud Delete State',
								'zAddAssetAttr-PTP Trashed State',
								'zIntResou-PTP Trashed State',
								'zIntResou-Cloud Delete Asset UUID With Resource Type',
								'zMedAnlyAstAttr-Media Analysis Timestamp',
								'zAsset-Analysis State Modificaion Date',
								'zAddAssetAttr- Pending View Count',
								'zAddAssetAttr- View Count',
								'zAddAssetAttr- Pending Play Count',
								'zAddAssetAttr- Play Count',
								'zAddAssetAttr- Pending Share Count',
								'zAddAssetAttr- Share Count',
								'zAddAssetAttr-Allowed for Analysis',
								'zAddAssetAttr-Scene Analysis Version',
								'zAddAssetAttr-Scene Analysis is From Preview',
								'zAddAssetAttr-Scene Analysis Timestamp',
								'zAsset-Duplication Asset Visibility State',
								'zAddAssetAttr-Destination Asset Copy State',
								'zAddAssetAttr-Duplicate Detector Perceptual Processing State',
								'zAddAssetAttr-Source Asset for Duplication Scope ID',
								'zCldMast-Source Master For Duplication Scope ID',
								'zAddAssetAttr-Source Asset For Duplication ID',
								'zCldMast-Source Master for Duplication ID',
								'zAddAssetAttr-Variation Suggestions States',
								'zAsset-High Frame Rate State',
								'zAsset-Video Key Frame Time Scale',
								'zAsset-Video Key Frame Value',
								'zExtAttr-ISO',
								'zExtAttr-Metering Mode',
								'zExtAttr-Sample Rate',
								'zExtAttr-Track Format',
								'zExtAttr-White Balance',
								'zExtAttr-Aperture',
								'zExtAttr-BitRate',
								'zExtAttr-Exposure Bias',
								'zExtAttr-Frames Per Second',
								'zExtAttr-Shutter Speed',
								'zExtAttr-Slush Scene Bias',
								'zExtAttr-Slush Version',
								'zExtAttr-Slush Preset',
								'zExtAttr-Slush Warm Bias',
								'zAsset-Height',
								'zAddAssetAttr-Original Height',
								'zIntResou-Unoriented Height',
								'zAsset-Width',
								'zAddAssetAttr-Original Width',
								'zIntResou-Unoriented Width',
								'zAsset-Thumbnail Index',
								'zAddAssetAttr-Embedded Thumbnail Height',
								'zAddAssetAttr-Embedded Thumbnail Length',
								'zAddAssetAttr-Embedded Thumbnail Offset',
								'zAddAssetAttr-Embedded Thumbnail Width',
								'zAsset-Packed Acceptable Crop Rect',
								'zAsset-Packed Badge Attributes',
								'zAsset-Packed Preferred Crop Rect',
								'zAsset-Curation Score',
								'zAsset-Camera Processing Adjustment State',
								'zAsset-Depth Type',
								'zAsset-Is Magic Carpet-QuicktimeMOVfile',
								'zAddAssetAttr-Orig Resource Choice',
								'zAsset-Spatial Type',
								'zAddAssetAttr-Spatial Over Capture Group ID',
								'zAddAssetAttr-Place Annotation Data',
								'zAddAssetAttr-Edited IPTC Attributes',
								'zAddAssetAttr-Title/Comments via Cloud Website',
								'zAddAssetAttr-Accessibility Description',
								'zAddAssetAttr-Photo Stream Tag ID',
								'zAddAssetAttr-Share Type',
								'zAddAssetAttr-Library Scope Asset Contributors To Update',
								'zAsset-Overall Aesthetic Score',
								'zAsset-zENT',
								'zAsset-zOPT',
								'zAsset-Master= zCldMast-zPK',
								'zAsset-Extended Attributes= zExtAttr-zPK',
								'zAsset-Import Session Key',
								'zAsset-Photo Analysis Attributes Key',
								'zAsset-FOK-Cloud Feed Asset Entry Key',
								'zAsset-Computed Attributes Asset Key',
								'zAsset-Promotion Score',
								'zAsset-Iconic Score',
								'zAsset-Media Analysis Attributes Key',
								'zAsset-Media Group UUID',
								'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
								'zAsset.Cloud Collection GUID',
								'zAddAssetAttr-zENT',
								'ZAddAssetAttr-zOPT',
								'zAddAssetAttr-zAsset= zAsset_zPK',
								'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
								'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
								'zAddAssetAttr-Public Global UUID',
								'zAddAssetAttr-Original Assets UUID',
								'zAddAssetAttr-Originating Asset Identifier',
								'zAddAssetAttr.Adjusted Fingerprint',
								'zCldMast-zPK= zAsset-Master',
								'zCldMast-zENT',
								'zCldMast-zOPT',
								'zCldMast-Moment Share Key= zShare-zPK',
								'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
								'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
								'zCldMast-Originating Asset ID',
								'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
								'CMzCldMastMedData-zENT',
								'CMzCldMastMedData-CldMast= zCldMast-zPK',
								'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
								'AAAzCldMastMedData-zENT',
								'AAAzCldMastMedData-CldMast key',
								'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
								'zExtAttr-zPK= zAsset-zExtendedAttributes',
								'zExtAttr-zENT',
								'zExtAttr-zOPT',
								'zExtAttr-Asset Key',
								'zIntResou-zPK',
								'zIntResou-zENT',
								'zIntResou-zOPT',
								'zIntResou-Asset= zAsset_zPK',
								'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
								'zMedAnlyAstAttr-zEnt',
								'zMedAnlyAstAttr-zOpt',
								'zMedAnlyAstAttr-Asset= zAsset-zPK')
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = 'Ph50.2-Asset_IntResou-SyndPL'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = 'Ph50.2-Asset_IntResou-SyndPL'
				timeline(report_folder, tlactivity, data_list, data_headers)

			else:
				logfunc('No Internal Resource data available for iOS 17 Syndication Photos Library Photos.sqlite')

			db.close()
			return


__artifacts_v2__ = {
	'Ph50-1-Asset_IntResou-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite 50.1 Asset IntResource Optimization Data',
		'description': 'Parses iOS 17 asset records from PhotoData/Photos.sqlite ZINTERNALRESOURCE'
					   ' and other tables. This and other related parsers should provide data for investigative'
					   ' analysis of assets being stored locally on the device verses assets being stored in'
					   ' iCloud Photos as the result of optimization. This is very large query and script,'
					   ' I recommend opening the TSV generated report with Zimmermans Tools'
					   ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
					   ' and filter the results.',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '1.0',
		'date': '2024-04-19',
		'requirements': 'Acquisition that contains PhotoData/Photos.sqlite',
		'category': 'Photos.sqlite-Asset_IntResou-Optimization',
		'notes': '',
		'paths': ('*/mobile/Media/PhotoData/Photos.sqlite*'),
		'function': 'get_ph50intresouoptimzdataphdapsql'
	},
	'Ph50-2-Asset_IntResou-SyndPL': {
		'name': 'SyndPL Photos.sqlite 50.2 Asset IntResource Optimization Data',
		'description': 'Parses iOS 17 asset records from Syndication.photos.library/database/Photos.sqlite ZINTERNALRESOURCE and'
					   ' and other tables. This and other related parsers should provide data for investigative'
					   ' analysis of assets being stored locally on the device verses assets being stored in'
					   ' iCloud Photos as the result of optimization. This is very large query and script,'
					   ' I recommend opening the TSV generated report with Zimmermans Tools'
					   ' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
					   ' and filter the results.',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '1.0',
		'date': '2024-04-19',
		'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
		'category': 'Photos.sqlite-Syndication_PL_Artifacts',
		'notes': '',
		'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*'),
		'function': 'get_ph50intresouoptimzdatasyndpl'
	}
}