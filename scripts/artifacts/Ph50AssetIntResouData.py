# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses iOS 14-17 asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE and other tables.
#   This and other related parsers should provide data for investigative analysis of assets being stored locally
#   on the device verses assets being stored in iCloud Photos as the result of optimization.
#   This is very large query and script, I recommend opening the TSV generated report with Zimmerman's Tools
#   https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search and filter the results.
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
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
	if version.parse(iosversion) <= version.parse("13.7"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite ZINTERNALRESOURCE table data from iOS " + iosversion)
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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
		CASE zAsset.ZORIENTATION
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[236], row[237], row[238]))

				counter += 1

			description = 'Parses iOS 14 asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE and' \
				' other tables. This and other related parsers should provide data for investigative' \
				' analysis of assets being stored locally on the device verses assets being stored in' \
				' iCloud Photos as the result of optimization. This is very large query and script I' \
				' recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
							'zIntResou-Local Availability-4QueryStart-1',
							'zIntResou-Remote Availability-4QueryStart-2',
							'zIntResou-Resource Type-4QueryStart-3',
							'zIntResou-Datastore Sub-Type-4QueryStart-4',
							'zIntResou-Recipe ID-4QueryStart-5',
							'zAsset Complete-6',
							'zAsset-zPK-7',
							'zAddAssetAttr-zPK-8',
							'zAsset-UUID = store.cloudphotodb-9',
							'zAddAssetAttr-Master Fingerprint-10',
							'zIntResou-Fingerprint-11',
							'zAsset-Cloud is My Asset-12',
							'zAsset-Cloud is deletable-Asset-13',
							'zAsset-Cloud_Local_State-14',
							'zAsset-Visibility State-15',
							'zExtAttr-Camera Make-16',
							'zExtAttr-Camera Model-17',
							'zExtAttr-Lens Model-18',
							'zExtAttr-Flash Fired-19',
							'zExtAttr-Focal Lenght-20',
							'zAsset-Derived Camera Capture Device-21',
							'zAddAssetAttr-Camera Captured Device-22',
							'zAddAssetAttr-Imported by-23',
							'zCldMast-Imported By-24',
							'zAddAssetAttr-Creator Bundle ID-25',
							'zAddAssetAttr-Imported By Display Name-26',
							'zCldMast-Imported by Bundle ID-27',
							'zCldMast-Imported by Display Name-28',
							'zAsset-Saved Asset Type-29',
							'zAsset-Directory-Path-30',
							'zAsset-Filename-31',
							'zAddAssetAttr- Original Filename-32',
							'zCldMast- Original Filename-33',
							'zAsset-Added Date-34',
							'zAsset- SortToken -CameraRoll-35',
							'zAsset-Date Created-36',
							'zCldMast-Creation Date-37',
							'zIntResou-CldMst Date Created-38',
							'zAddAssetAttr-Time Zone Name-39',
							'zAddAssetAttr-Time Zone Offset-40',
							'zAddAssetAttr-Inferred Time Zone Offset-41',
							'zAddAssetAttr-EXIF-String-42',
							'zAsset-Modification Date-43',
							'zAsset-Last Shared Date-44',
							'zCldMast-Cloud Local State-45',
							'zCldMast-Import Date-46',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-47',
							'zAddAssetAttr-Import Session ID-48',
							'zAddAssetAttr-Alt Import Image Date-49',
							'zCldMast-Import Session ID- AirDrop-StillTesting-50',
							'zAsset-Cloud Batch Publish Date-51',
							'zAsset-Cloud Server Publish Date-52',
							'zAsset-Cloud Download Requests-53',
							'zAsset-Cloud Batch ID-54',
							'zAddAssetAttr-Upload Attempts-55',
							'zAsset-Latitude-56',
							'zExtAttr-Latitude-57',
							'zAsset-Longitude-58',
							'zExtAttr-Longitude-59',
							'zAddAssetAttr-GPS Horizontal Accuracy-60',
							'zAddAssetAttr-Location Hash-61',
							'zAddAssetAttr-Shifted Location Valid-62',
							'zAddAssetAttr-Shifted Location Data-63',
							'zAddAssetAttr-Reverse Location Is Valid-64',
							'zAddAssetAttr-Reverse Location Data-65',
							'AAAzCldMastMedData-zOPT-66',
							'zAddAssetAttr-Media Metadata Type-67',
							'AAAzCldMastMedData-Data-68',
							'CldMasterzCldMastMedData-zOPT-69',
							'zCldMast-Media Metadata Type-70',
							'CMzCldMastMedData-Data-71',
							'zAsset-Orientation-72',
							'zAddAssetAttr-Original Orientation-73',
							'zAsset-Kind-74',
							'zAsset-Kind-Sub-Type-75',
							'zAddAssetAttr-Cloud Kind Sub Type-76',
							'zAsset-Playback Style-77',
							'zAsset-Playback Variation-78',
							'zAsset-Video Duration-79',
							'zExtAttr-Duration-80',
							'zAsset-Video CP Duration-81',
							'zAddAssetAttr-Video CP Duration Time Scale-82',
							'zAsset-Video CP Visibility State-83',
							'zAddAssetAttr-Video CP Display Value-84',
							'zAddAssetAttr-Video CP Display Time Scale-85',
							'zIntResou-Datastore Class ID-86',
							'zAsset-Cloud Placeholder Kind-87',
							'zIntResou-Local Availability-88',
							'zIntResou-Local Availability Target-89',
							'zIntResou-Cloud Local State-90',
							'zIntResou-Remote Availability-91',
							'zIntResou-Remote Availability Target-92',
							'zIntResou-Transient Cloud Master-93',
							'zIntResou-Side Car Index-94',
							'zIntResou- File ID-95',
							'zIntResou-Version-96',
							'zAddAssetAttr- Original-File-Size-97',
							'zIntResou-Resource Type-98',
							'zIntResou-Datastore Sub-Type-99',
							'zIntResou-Cloud Source Type-100',
							'zIntResou-Data Length-101',
							'zIntResou-Recipe ID-102',
							'zIntResou-Cloud Last Prefetch Date-103',
							'zIntResou-Cloud Prefetch Count-104',
							'zIntResou- Cloud-Last-OnDemand Download-Date-105',
							'zAsset-Uniform Type ID-106',
							'zAsset-Original Color Space-107',
							'zCldMast-Uniform_Type_ID-108',
							'zCldMast-Full Size JPEG Source-109',
							'zAsset-HDR Gain-110',
							'zExtAttr-Codec-111',
							'zCldMast-Codec Name-112',
							'zCldMast-Video Frame Rate-113',
							'zCldMast-Placeholder State-114',
							'zAsset-Depth_Type-115',
							'zAsset-Avalanche UUID-116',
							'zAsset-Avalanche_Pick_Type-BurstAsset-117',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-118',
							'zAddAssetAttr-Cloud Recovery State-119',
							'zAddAssetAttr-Cloud State Recovery Attempts Count-120',
							'zAsset-Deferred Processing Needed-121',
							'zAddAssetAttr-Deferred Photo Identifier-122',
							'zAddAssetAttr-Deferred Processing Candidate Options-123',
							'zAsset-Has Adjustments-Camera-Effects-Filters-124',
							'zAsset-Adjustment Timestamp-125',
							'zAddAssetAttr-Editor Bundle ID-126',
							'zAddAssetAttr-Montage-127',
							'zAsset-Favorite-128',
							'zAsset-Hidden-129',
							'zAsset-Trashed State-LocalAssetRecentlyDeleted-130',
							'zAsset-Trashed Date-131',
							'zIntResou-Trash State-132',
							'zIntResou-Trashed Date-133',
							'zAsset-Cloud Delete State-134',
							'zIntResou-Cloud Delete State-135',
							'zAddAssetAttr-PTP Trashed State-136',
							'zIntResou-PTP Trashed State-137',
							'zIntResou-Cloud Delete Asset UUID With Resource Type-138',
							'zMedAnlyAstAttr-Media Analysis Timestamp-139',
							'zAsset-Analysis State Modificaion Date-140',
							'zAddAssetAttr- Pending View Count-141',
							'zAddAssetAttr- View Count-142',
							'zAddAssetAttr- Pending Play Count-143',
							'zAddAssetAttr- Play Count-144',
							'zAddAssetAttr- Pending Share Count-145',
							'zAddAssetAttr- Share Count-146',
							'zAddAssetAttr-Allowed for Analysis-147',
							'zAddAssetAttr-Scene Analysis Version-148',
							'zAddAssetAttr-Scene Analysis Timestamp-149',
							'zAddAssetAttr-Destination Asset Copy State-150',
							'zAddAssetAttr-Variation Suggestions States-151',
							'zAsset-High Frame Rate State-152',
							'zAsset-Video Key Frame Time Scale-153',
							'zAsset-Video Key Frame Value-154',
							'zExtAttr-ISO-155',
							'zExtAttr-Metering Mode-156',
							'zExtAttr-Sample Rate-157',
							'zExtAttr-Track Format-158',
							'zExtAttr-White Balance-159',
							'zExtAttr-Aperture-160',
							'zExtAttr-BitRate-161',
							'zExtAttr-Exposure Bias-162',
							'zExtAttr-Frames Per Second-163',
							'zExtAttr-Shutter Speed-164',
							'zAsset-Height-165',
							'zAddAssetAttr-Original Height-166',
							'zIntResou-Unoriented Height-167',
							'zAsset-Width-168',
							'zAddAssetAttr-Original Width-169',
							'zIntResou-Unoriented Width-170',
							'zAsset-Thumbnail Index-171',
							'zAddAssetAttr-Embedded Thumbnail Height-172',
							'zAddAssetAttr-Embedded Thumbnail Length-173',
							'zAddAssetAttr-Embedded Thumbnail Offset-174',
							'zAddAssetAttr-Embedded Thumbnail Width-175',
							'zAsset-Packed Acceptable Crop Rect-176',
							'zAsset-Packed Badge Attributes-177',
							'zAsset-Packed Preferred Crop Rect-178',
							'zAsset-Curation Score-179',
							'zAsset-Camera Processing Adjustment State-180',
							'zAsset-Depth Type-181',
							'zAddAssetAttr-Orig Resource Choice-182',
							'zAddAssetAttr-Spatial Over Capture Group ID-183',
							'zAddAssetAttr-Place Annotation Data-184',
							'zAddAssetAttr-Distance Identity-HEX-185',
							'zAddAssetAttr-Edited IPTC Attributes-186',
							'zAddAssetAttr-Title-Comments via Cloud Website-187',
							'zAddAssetAttr-Accessibility Description-188',
							'zAddAssetAttr-Photo Stream Tag ID-189',
							'zAddAssetAttr-Share Type-190',
							'zAsset-Overall Aesthetic Score-191',
							'zAsset-zENT-192',
							'zAsset-zOPT-193',
							'zAsset-Master= zCldMast-zPK-194',
							'zAsset-Extended Attributes= zExtAttr-zPK-195',
							'zAsset-Import Session Key-196',
							'zAsset-FOK-Cloud Feed Asset Entry Key-197',
							'zAsset-Computed Attributes Asset Key-198',
							'zAsset-Promotion Score-199',
							'zAsset-Media Analysis Attributes Key-200',
							'zAsset-Media Group UUID-201',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb-202',
							'zAsset.Cloud Collection GUID-203',
							'zAddAssetAttr-zENT-204',
							'ZAddAssetAttr-zOPT-205',
							'zAddAssetAttr-zAsset= zAsset_zPK-206',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-207',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-208',
							'zAddAssetAttr-Public Global UUID-209',
							'zAddAssetAttr-Original Assets UUID-210',
							'zAddAssetAttr-Originating Asset Identifier-211',
							'zAddAssetAttr.Adjusted Fingerprint-212',
							'zCldMast-zPK= zAsset-Master-213',
							'zCldMast-zENT-214',
							'zCldMast-zOPT-215',
							'zCldMast-Moment Share Key= zShare-zPK-216',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-217',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb-218',
							'zCldMast-Originating Asset ID-219',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-220',
							'CMzCldMastMedData-zENT-221',
							'CMzCldMastMedData-CldMast= zCldMast-zPK-222',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-223',
							'AAAzCldMastMedData-zENT-224',
							'AAAzCldMastMedData-CldMast key-225',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-226',
							'zExtAttr-zPK= zAsset-zExtendedAttributes-227',
							'zExtAttr-zENT-228',
							'zExtAttr-zOPT-229',
							'zExtAttr-Asset Key-230',
							'zIntResou-zPK-231',
							'zIntResou-zENT-232',
							'zIntResou-zOPT-233',
							'zIntResou-Asset= zAsset_zPK-234',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-235',
							'zMedAnlyAstAttr-zEnt-236',
							'zMedAnlyAstAttr-zOpt-237',
							'zMedAnlyAstAttr-Asset= zAsset-zPK-238')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 14 PhotoData-Photos.sqlite')

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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG-THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG-HEIC-quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj-Mutation_Data-37'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[252], row[253], row[254], row[255], row[256], row[257], row[258], row[259],
								row[260], row[261], row[262]))

				counter += 1

			description = 'Parses iOS 15 asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE and' \
' other tables. This and other related parsers should provide data for investigative' \
' analysis of assets being stored locally on the device verses assets being stored in' \
' iCloud Photos as the result of optimization. This is very large query and script,' \
' I recommend opening the TSV generated report with Zimmermans Tools' \
' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search, and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
							'zIntResou-Local Availability-4QueryStart-1',
							'zIntResou-Remote Availability-4QueryStart-2',
							'zIntResou-Resource Type-4QueryStart-3',
							'zIntResou-Datastore Sub-Type-4QueryStart-4',
							'zIntResou-Recipe ID-4QueryStart-5',
							'zAsset Complete-6',
							'zAsset-zPK-7',
							'zAddAssetAttr-zPK-8',
							'zAsset-UUID = store.cloudphotodb-9',
							'zAddAssetAttr-Master Fingerprint-10',
							'zIntResou-Fingerprint-11',
							'zAsset-Bundle Scope-12',
							'zAsset-Syndication State-13',
							'zAsset-Cloud is My Asset-14',
							'zAsset-Cloud is deletable-Asset-15',
							'zAsset-Cloud_Local_State-16',
							'zAsset-Visibility State-17',
							'zExtAttr-Camera Make-18',
							'zExtAttr-Camera Model-19',
							'zExtAttr-Lens Model-20',
							'zExtAttr-Flash Fired-21',
							'zExtAttr-Focal Lenght-22',
							'zExtAttr-Focal Lenth in 35MM-23',
							'zExtAttr-Digital Zoom Ratio-24',
							'zAsset-Derived Camera Capture Device-25',
							'zAddAssetAttr-Camera Captured Device-26',
							'zAddAssetAttr-Imported by-27',
							'zCldMast-Imported By-28',
							'zAddAssetAttr.Imported by Bundle Identifier-29',
							'zAddAssetAttr-Imported By Display Name-30',
							'zCldMast-Imported by Bundle ID-31',
							'zCldMast-Imported by Display Name-32',
							'zAsset-Saved Asset Type-33',
							'zAsset-Directory-Path-34',
							'zAsset-Filename-35',
							'zAddAssetAttr- Original Filename-36',
							'zCldMast- Original Filename-37',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-38',
							'zAsset-Added Date-39',
							'zAsset- SortToken -CameraRoll-40',
							'zAddAssetAttr-Date Created Source-41',
							'zAsset-Date Created-42',
							'zCldMast-Creation Date-43',
							'zIntResou-CldMst Date Created-44',
							'zAddAssetAttr-Time Zone Name-45',
							'zAddAssetAttr-Time Zone Offset-46',
							'zAddAssetAttr-Inferred Time Zone Offset-47',
							'zAddAssetAttr-EXIF-String-48',
							'zAsset-Modification Date-49',
							'zAsset-Last Shared Date-50',
							'zCldMast-Cloud Local State-51',
							'zCldMast-Import Date-52',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-53',
							'zAddAssetAttr-Import Session ID-54',
							'zAddAssetAttr-Alt Import Image Date-55',
							'zCldMast-Import Session ID- AirDrop-StillTesting-56',
							'zAsset-Cloud Batch Publish Date-57',
							'zAsset-Cloud Server Publish Date-58',
							'zAsset-Cloud Download Requests-59',
							'zAsset-Cloud Batch ID-60',
							'zAddAssetAttr-Upload Attempts-61',
							'zAsset-Latitude-62',
							'zExtAttr-Latitude-63',
							'zAsset-Longitude-64',
							'zExtAttr-Longitude-65',
							'zAddAssetAttr-GPS Horizontal Accuracy-66',
							'zAddAssetAttr-Location Hash-67',
							'zAddAssetAttr-Shifted Location Valid-68',
							'zAddAssetAttr-Shifted Location Data-69',
							'zAddAssetAttr-Reverse Location Is Valid-70',
							'zAddAssetAttr-Reverse Location Data-71',
							'AAAzCldMastMedData-zOPT-72',
							'zAddAssetAttr-Media Metadata Type-73',
							'AAAzCldMastMedData-Data-74',
							'CldMasterzCldMastMedData-zOPT-75',
							'zCldMast-Media Metadata Type-76',
							'CMzCldMastMedData-Data-77',
							'zAddAssetAttr-Syndication History-78',
							'zMedAnlyAstAttr-Syndication Processing Version-79',
							'zMedAnlyAstAttr-Syndication Processing Value-80',
							'zAsset-Orientation-81',
							'zAddAssetAttr-Original Orientation-82',
							'zAsset-Kind-83',
							'zAsset-Kind-Sub-Type-84',
							'zAddAssetAttr-Cloud Kind Sub Type-85',
							'zAsset-Playback Style-86',
							'zAsset-Playback Variation-87',
							'zAsset-Video Duration-88',
							'zExtAttr-Duration-89',
							'zAsset-Video CP Duration-90',
							'zAddAssetAttr-Video CP Duration Time Scale-91',
							'zAsset-Video CP Visibility State-92',
							'zAddAssetAttr-Video CP Display Value-93',
							'zAddAssetAttr-Video CP Display Time Scale-94',
							'zIntResou-Datastore Class ID-95',
							'zAsset-Cloud Placeholder Kind-96',
							'zIntResou-Local Availability-97',
							'zIntResou-Local Availability Target-98',
							'zIntResou-Cloud Local State-99',
							'zIntResou-Remote Availability-100',
							'zIntResou-Remote Availability Target-101',
							'zIntResou-Transient Cloud Master-102',
							'zIntResou-Side Car Index-103',
							'zIntResou- File ID-104',
							'zIntResou-Version-105',
							'zAddAssetAttr- Original-File-Size-106',
							'zIntResou-Resource Type-107',
							'zIntResou-Datastore Sub-Type-108',
							'zIntResou-Cloud Source Type-109',
							'zIntResou-Data Length-110',
							'zIntResou-Recipe ID-111',
							'zIntResou-Cloud Last Prefetch Date-112',
							'zIntResou-Cloud Prefetch Count-113',
							'zIntResou- Cloud-Last-OnDemand Download-Date-114',
							'zIntResou-UniformTypeID_UTI_Conformance_Hint-115',
							'zIntResou-Compact-UTI-116',
							'zAsset-Uniform Type ID-117',
							'zAsset-Original Color Space-118',
							'zCldMast-Uniform_Type_ID-119',
							'zCldMast-Full Size JPEG Source-120',
							'zAsset-HDR Gain-121',
							'zAsset-zHDR_Type-122',
							'zExtAttr-Codec-123',
							'zIntResou-Codec Four Char Code Name-124',
							'zCldMast-Codec Name-125',
							'zCldMast-Video Frame Rate-126',
							'zCldMast-Placeholder State-127',
							'zAsset-Depth_Type-128',
							'zAsset-Avalanche UUID-129',
							'zAsset-Avalanche_Pick_Type-BurstAsset-130',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-131',
							'zAddAssetAttr-Cloud Recovery State-132',
							'zAddAssetAttr-Cloud State Recovery Attempts Count-133',
							'zAsset-Deferred Processing Needed-134',
							'zAsset-Video Deferred Processing Needed-135',
							'zAddAssetAttr-Deferred Photo Identifier-136',
							'zAddAssetAttr-Deferred Processing Candidate Options-137',
							'zAsset-Has Adjustments-Camera-Effects-Filters-138',
							'zAsset-Adjustment Timestamp-139',
							'zAddAssetAttr-Editor Bundle ID-140',
							'zAddAssetAttr-Montage-141',
							'zAsset-Favorite-142',
							'zAsset-Hidden-143',
							'zAsset-Trashed State-LocalAssetRecentlyDeleted-144',
							'zAsset-Trashed Date-145',
							'zIntResou-Trash State-146',
							'zIntResou-Trashed Date-147',
							'zAsset-Cloud Delete State-148',
							'zIntResou-Cloud Delete State-149',
							'zAddAssetAttr-PTP Trashed State-150',
							'zIntResou-PTP Trashed State-151',
							'zIntResou-Cloud Delete Asset UUID With Resource Type-152',
							'zMedAnlyAstAttr-Media Analysis Timestamp-153',
							'zAsset-Analysis State Modificaion Date-154',
							'zAddAssetAttr- Pending View Count-155',
							'zAddAssetAttr- View Count-156',
							'zAddAssetAttr- Pending Play Count-157',
							'zAddAssetAttr- Play Count-158',
							'zAddAssetAttr- Pending Share Count-159',
							'zAddAssetAttr- Share Count-160',
							'zAddAssetAttr-Allowed for Analysis-161',
							'zAddAssetAttr-Scene Analysis Version-162',
							'zAddAssetAttr-Scene Analysis is From Preview-163',
							'zAddAssetAttr-Scene Analysis Timestamp-164',
							'zAddAssetAttr-Destination Asset Copy State-165',
							'zAddAssetAttr-Source Asset for Duplication Scope ID-166',
							'zCldMast-Source Master For Duplication Scope ID-167',
							'zAddAssetAttr-Source Asset For Duplication ID-168',
							'zCldMast-Source Master for Duplication ID-169',
							'zAddAssetAttr-Variation Suggestions States-170',
							'zAsset-High Frame Rate State-171',
							'zAsset-Video Key Frame Time Scale-172',
							'zAsset-Video Key Frame Value-173',
							'zExtAttr-ISO-174',
							'zExtAttr-Metering Mode-175',
							'zExtAttr-Sample Rate-176',
							'zExtAttr-Track Format-177',
							'zExtAttr-White Balance-178',
							'zExtAttr-Aperture-179',
							'zExtAttr-BitRate-180',
							'zExtAttr-Exposure Bias-181',
							'zExtAttr-Frames Per Second-182',
							'zExtAttr-Shutter Speed-183',
							'zExtAttr-Slush Scene Bias-184',
							'zExtAttr-Slush Version-185',
							'zExtAttr-Slush Preset-186',
							'zExtAttr-Slush Warm Bias-187',
							'zAsset-Height-188',
							'zAddAssetAttr-Original Height-189',
							'zIntResou-Unoriented Height-190',
							'zAsset-Width-191',
							'zAddAssetAttr-Original Width-192',
							'zIntResou-Unoriented Width-193',
							'zAsset-Thumbnail Index-194',
							'zAddAssetAttr-Embedded Thumbnail Height-195',
							'zAddAssetAttr-Embedded Thumbnail Length-196',
							'zAddAssetAttr-Embedded Thumbnail Offset-197',
							'zAddAssetAttr-Embedded Thumbnail Width-198',
							'zAsset-Packed Acceptable Crop Rect-199',
							'zAsset-Packed Badge Attributes-200',
							'zAsset-Packed Preferred Crop Rect-201',
							'zAsset-Curation Score-202',
							'zAsset-Camera Processing Adjustment State-203',
							'zAsset-Depth Type-204',
							'zAsset-Is Magic Carpet-QuicktimeMOVfile-205',
							'zAddAssetAttr-Orig Resource Choice-206',
							'zAddAssetAttr-Spatial Over Capture Group ID-207',
							'zAddAssetAttr-Place Annotation Data-208',
							'zAddAssetAttr-Distance Identity-HEX-209',
							'zAddAssetAttr-Edited IPTC Attributes-210',
							'zAddAssetAttr-Title-Comments via Cloud Website-211',
							'zAddAssetAttr-Accessibility Description-212',
							'zAddAssetAttr-Photo Stream Tag ID-213',
							'zAddAssetAttr-Share Type-214',
							'zAsset-Overall Aesthetic Score-215',
							'zAsset-zENT-216',
							'zAsset-zOPT-217',
							'zAsset-Master= zCldMast-zPK-218',
							'zAsset-Extended Attributes= zExtAttr-zPK-219',
							'zAsset-Import Session Key-220',
							'zAsset-FOK-Cloud Feed Asset Entry Key-221',
							'zAsset-Computed Attributes Asset Key-222',
							'zAsset-Promotion Score-223',
							'zAsset-Media Analysis Attributes Key-224',
							'zAsset-Media Group UUID-225',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb-226',
							'zAsset.Cloud Collection GUID-227',
							'zAddAssetAttr-zENT-228',
							'ZAddAssetAttr-zOPT-229',
							'zAddAssetAttr-zAsset= zAsset_zPK-230',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-231',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-232',
							'zAddAssetAttr-Public Global UUID-233',
							'zAddAssetAttr-Original Assets UUID-234',
							'zAddAssetAttr-Originating Asset Identifier-235',
							'zAddAssetAttr.Adjusted Fingerprint-236',
							'zCldMast-zPK= zAsset-Master-237',
							'zCldMast-zENT-238',
							'zCldMast-zOPT-239',
							'zCldMast-Moment Share Key= zShare-zPK-240',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-241',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb-242',
							'zCldMast-Originating Asset ID-243',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-244',
							'CMzCldMastMedData-zENT-245',
							'CMzCldMastMedData-CldMast= zCldMast-zPK-246',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-247',
							'AAAzCldMastMedData-zENT-248',
							'AAAzCldMastMedData-CldMast key-249',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-250',
							'zExtAttr-zPK= zAsset-zExtendedAttributes-251',
							'zExtAttr-zENT-252',
							'zExtAttr-zOPT-253',
							'zExtAttr-Asset Key-254',
							'zIntResou-zPK-255',
							'zIntResou-zENT-256',
							'zIntResou-zOPT-257',
							'zIntResou-Asset= zAsset_zPK-258',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-259',
							'zMedAnlyAstAttr-zEnt-260',
							'zMedAnlyAstAttr-zOpt-261',
							'zMedAnlyAstAttr-Asset= zAsset-zPK-262')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 15 PhotoData-Photos.sqlite')

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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG-THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG-HEIC-quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj-Mutation_Data-37'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		CASE zAsset.ZDELETEREASON
			WHEN 1 THEN '1-StillTesting Delete-Reason-1'
			WHEN 2 THEN '2-StillTesting Delete-Reason-2'
			WHEN 3 THEN '3-StillTesting Delete-Reason-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
		END AS 'zAsset-Delete-Reason',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[260], row[261], row[262], row[263], row[264], row[265], row[266], row[267],
								row[268], row[269], row[270], row[271]))

				counter += 1

			description = 'Parses iOS 16 asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE and' \
' other tables. This and other related parsers should provide data for investigative' \
' analysis of assets being stored locally on the device verses assets being stored in' \
' iCloud Photos as the result of optimization. This is very large query and script,' \
' I recommend opening the TSV generated report with Zimmermans Tools' \
' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
							'zIntResou-Local Availability-4QueryStart-1',
							'zIntResou-Remote Availability-4QueryStart-2',
							'zIntResou-Resource Type-4QueryStart-3',
							'zIntResou-Datastore Sub-Type-4QueryStart-4',
							'zIntResou-Recipe ID-4QueryStart-5',
							'zAsset Complete-6',
							'zAsset-zPK-7',
							'zAddAssetAttr-zPK-8',
							'zAsset-UUID = store.cloudphotodb-9',
							'zAddAssetAttr-Master Fingerprint-10',
							'zIntResou-Fingerprint-11',
							'zAsset-Bundle Scope-12',
							'zAsset-Syndication State-13',
							'zAsset-Cloud is My Asset-14',
							'zAsset-Cloud is deletable-Asset-15',
							'zAsset-Cloud_Local_State-16',
							'zAsset-Visibility State-17',
							'zExtAttr-Camera Make-18',
							'zExtAttr-Camera Model-19',
							'zExtAttr-Lens Model-20',
							'zExtAttr-Flash Fired-21',
							'zExtAttr-Focal Lenght-22',
							'zExtAttr-Focal Lenth in 35MM-23',
							'zExtAttr-Digital Zoom Ratio-24',
							'zAsset-Derived Camera Capture Device-25',
							'zAddAssetAttr-Camera Captured Device-26',
							'zAddAssetAttr-Imported by-27',
							'zCldMast-Imported By-28',
							'zAddAssetAttr.Imported by Bundle Identifier-29',
							'zAddAssetAttr-Imported By Display Name-30',
							'zCldMast-Imported by Bundle ID-31',
							'zCldMast-Imported by Display Name-32',
							'zAsset-Saved Asset Type-33',
							'zAsset-Directory-Path-34',
							'zAsset-Filename-35',
							'zAddAssetAttr- Original Filename-36',
							'zCldMast- Original Filename-37',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-38',
							'zAsset-Active Library Scope Participation State-39',
							'zAsset-Library Scope Share State- StillTesting-40',
							'zAsset-Added Date-41',
							'zAsset- SortToken -CameraRoll-42',
							'zAddAssetAttr-Date Created Source-43',
							'zAsset-Date Created-44',
							'zCldMast-Creation Date-45',
							'zIntResou-CldMst Date Created-46',
							'zAddAssetAttr-Time Zone Name-47',
							'zAddAssetAttr-Time Zone Offset-48',
							'zAddAssetAttr-Inferred Time Zone Offset-49',
							'zAddAssetAttr-EXIF-String-50',
							'zAsset-Modification Date-51',
							'zAsset-Last Shared Date-52',
							'zCldMast-Cloud Local State-53',
							'zCldMast-Import Date-54',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-55',
							'zAddAssetAttr-Import Session ID-56',
							'zAddAssetAttr-Alt Import Image Date-57',
							'zCldMast-Import Session ID- AirDrop-StillTesting-58',
							'zAsset-Cloud Batch Publish Date-59',
							'zAsset-Cloud Server Publish Date-60',
							'zAsset-Cloud Download Requests-61',
							'zAsset-Cloud Batch ID-62',
							'zAddAssetAttr-Upload Attempts-63',
							'zAsset-Latitude-64',
							'zExtAttr-Latitude-65',
							'zAsset-Longitude-66',
							'zExtAttr-Longitude-67',
							'zAddAssetAttr-GPS Horizontal Accuracy-68',
							'zAddAssetAttr-Location Hash-69',
							'zAddAssetAttr-Shifted Location Valid-70',
							'zAddAssetAttr-Shifted Location Data-71',
							'zAddAssetAttr-Reverse Location Is Valid-72',
							'zAddAssetAttr-Reverse Location Data-73',
							'AAAzCldMastMedData-zOPT-74',
							'zAddAssetAttr-Media Metadata Type-75',
							'AAAzCldMastMedData-Data-76',
							'CldMasterzCldMastMedData-zOPT-77',
							'zCldMast-Media Metadata Type-78',
							'CMzCldMastMedData-Data-79',
							'zAsset-Search Index Rebuild State-80',
							'zAddAssetAttr-Syndication History-81',
							'zMedAnlyAstAttr-Syndication Processing Version-82',
							'zMedAnlyAstAttr-Syndication Processing Value-83',
							'zAsset-Orientation-84',
							'zAddAssetAttr-Original Orientation-85',
							'zAsset-Kind-86',
							'zAsset-Kind-Sub-Type-87',
							'zAddAssetAttr-Cloud Kind Sub Type-88',
							'zAsset-Playback Style-89',
							'zAsset-Playback Variation-90',
							'zAsset-Video Duration-91',
							'zExtAttr-Duration-92',
							'zAsset-Video CP Duration-93',
							'zAddAssetAttr-Video CP Duration Time Scale-94',
							'zAsset-Video CP Visibility State-95',
							'zAddAssetAttr-Video CP Display Value-96',
							'zAddAssetAttr-Video CP Display Time Scale-97',
							'zIntResou-Datastore Class ID-98',
							'zAsset-Cloud Placeholder Kind-99',
							'zIntResou-Local Availability-100',
							'zIntResou-Local Availability Target-101',
							'zIntResou-Cloud Local State-102',
							'zIntResou-Remote Availability-103',
							'zIntResou-Remote Availability Target-104',
							'zIntResou-Transient Cloud Master-105',
							'zIntResou-Side Car Index-106',
							'zIntResou- File ID-107',
							'zIntResou-Version-108',
							'zAddAssetAttr- Original-File-Size-109',
							'zIntResou-Resource Type-110',
							'zIntResou-Datastore Sub-Type-111',
							'zIntResou-Cloud Source Type-112',
							'zIntResou-Data Length-113',
							'zIntResou-Recipe ID-114',
							'zIntResou-Cloud Last Prefetch Date-115',
							'zIntResou-Cloud Prefetch Count-116',
							'zIntResou- Cloud-Last-OnDemand Download-Date-117',
							'zIntResou-UniformTypeID_UTI_Conformance_Hint-118',
							'zIntResou-Compact-UTI-119',
							'zAsset-Uniform Type ID-120',
							'zAsset-Original Color Space-121',
							'zCldMast-Uniform_Type_ID-122',
							'zCldMast-Full Size JPEG Source-123',
							'zAsset-HDR Gain-124',
							'zAsset-zHDR_Type-125',
							'zExtAttr-Codec-126',
							'zIntResou-Codec Four Char Code Name-127',
							'zCldMast-Codec Name-128',
							'zCldMast-Video Frame Rate-129',
							'zCldMast-Placeholder State-130',
							'zAsset-Depth_Type-131',
							'zAsset-Avalanche UUID-132',
							'zAsset-Avalanche_Pick_Type-BurstAsset-133',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-134',
							'zAddAssetAttr-Cloud Recovery State-135',
							'zAddAssetAttr-Cloud State Recovery Attempts Count-136',
							'zAsset-Deferred Processing Needed-137',
							'zAsset-Video Deferred Processing Needed-138',
							'zAddAssetAttr-Deferred Photo Identifier-139',
							'zAddAssetAttr-Deferred Processing Candidate Options-140',
							'zAsset-Has Adjustments-Camera-Effects-Filters-141',
							'zAsset-Adjustment Timestamp-142',
							'zAddAssetAttr-Editor Bundle ID-143',
							'zAddAssetAttr-Montage-144',
							'zAsset-Favorite-145',
							'zAsset-Hidden-146',
							'zAsset-Trashed State-LocalAssetRecentlyDeleted-147',
							'zAsset-Trashed Date-148',
							'zAsset-Trashed by Participant= zSharePartic_zPK-149',
							'zAsset-Delete-Reason-150',
							'zIntResou-Trash State-151',
							'zIntResou-Trashed Date-152',
							'zAsset-Cloud Delete State-153',
							'zIntResou-Cloud Delete State-154',
							'zAddAssetAttr-PTP Trashed State-155',
							'zIntResou-PTP Trashed State-156',
							'zIntResou-Cloud Delete Asset UUID With Resource Type-157',
							'zMedAnlyAstAttr-Media Analysis Timestamp-158',
							'zAsset-Analysis State Modificaion Date-159',
							'zAddAssetAttr- Pending View Count-160',
							'zAddAssetAttr- View Count-161',
							'zAddAssetAttr- Pending Play Count-162',
							'zAddAssetAttr- Play Count-163',
							'zAddAssetAttr- Pending Share Count-164',
							'zAddAssetAttr- Share Count-165',
							'zAddAssetAttr-Allowed for Analysis-166',
							'zAddAssetAttr-Scene Analysis Version-167',
							'zAddAssetAttr-Scene Analysis is From Preview-168',
							'zAddAssetAttr-Scene Analysis Timestamp-169',
							'zAsset-Duplication Asset Visibility State-170',
							'zAddAssetAttr-Destination Asset Copy State-171',
							'zAddAssetAttr-Duplicate Detector Perceptual Processing State-172',
							'zAddAssetAttr-Source Asset for Duplication Scope ID-173',
							'zCldMast-Source Master For Duplication Scope ID-174',
							'zAddAssetAttr-Source Asset For Duplication ID-175',
							'zCldMast-Source Master for Duplication ID-176',
							'zAddAssetAttr-Variation Suggestions States-177',
							'zAsset-High Frame Rate State-178',
							'zAsset-Video Key Frame Time Scale-179',
							'zAsset-Video Key Frame Value-180',
							'zExtAttr-ISO-181',
							'zExtAttr-Metering Mode-182',
							'zExtAttr-Sample Rate-183',
							'zExtAttr-Track Format-184',
							'zExtAttr-White Balance-185',
							'zExtAttr-Aperture-186',
							'zExtAttr-BitRate-187',
							'zExtAttr-Exposure Bias-188',
							'zExtAttr-Frames Per Second-189',
							'zExtAttr-Shutter Speed-190',
							'zExtAttr-Slush Scene Bias-191',
							'zExtAttr-Slush Version-192',
							'zExtAttr-Slush Preset-193',
							'zExtAttr-Slush Warm Bias-194',
							'zAsset-Height-195',
							'zAddAssetAttr-Original Height-196',
							'zIntResou-Unoriented Height-197',
							'zAsset-Width-198',
							'zAddAssetAttr-Original Width-199',
							'zIntResou-Unoriented Width-200',
							'zAsset-Thumbnail Index-201',
							'zAddAssetAttr-Embedded Thumbnail Height-202',
							'zAddAssetAttr-Embedded Thumbnail Length-203',
							'zAddAssetAttr-Embedded Thumbnail Offset-204',
							'zAddAssetAttr-Embedded Thumbnail Width-205',
							'zAsset-Packed Acceptable Crop Rect-206',
							'zAsset-Packed Badge Attributes-207',
							'zAsset-Packed Preferred Crop Rect-208',
							'zAsset-Curation Score-209',
							'zAsset-Camera Processing Adjustment State-210',
							'zAsset-Depth Type-211',
							'zAsset-Is Magic Carpet-QuicktimeMOVfile-212',
							'zAddAssetAttr-Orig Resource Choice-213',
							'zAddAssetAttr-Spatial Over Capture Group ID-214',
							'zAddAssetAttr-Place Annotation Data-215',
							'zAddAssetAttr-Distance Identity-HEX-216',
							'zAddAssetAttr-Edited IPTC Attributes-217',
							'zAddAssetAttr-Title-Comments via Cloud Website-218',
							'zAddAssetAttr-Accessibility Description-219',
							'zAddAssetAttr-Photo Stream Tag ID-220',
							'zAddAssetAttr-Share Type-221',
							'zAddAssetAttr-Library Scope Asset Contributors To Update-222',
							'zAsset-Overall Aesthetic Score-223',
							'zAsset-zENT-224',
							'zAsset-zOPT-225',
							'zAsset-Master= zCldMast-zPK-226',
							'zAsset-Extended Attributes= zExtAttr-zPK-227',
							'zAsset-Import Session Key-228',
							'zAsset-Photo Analysis Attributes Key-229',
							'zAsset-FOK-Cloud Feed Asset Entry Key-230',
							'zAsset-Computed Attributes Asset Key-231',
							'zAsset-Promotion Score-232',
							'zAsset-Media Analysis Attributes Key-233',
							'zAsset-Media Group UUID-234',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb-235',
							'zAsset.Cloud Collection GUID-236',
							'zAddAssetAttr-zENT-237',
							'ZAddAssetAttr-zOPT-238',
							'zAddAssetAttr-zAsset= zAsset_zPK-239',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-240',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-241',
							'zAddAssetAttr-Public Global UUID-242',
							'zAddAssetAttr-Original Assets UUID-243',
							'zAddAssetAttr-Originating Asset Identifier-244',
							'zAddAssetAttr.Adjusted Fingerprint-245',
							'zCldMast-zPK= zAsset-Master-246',
							'zCldMast-zENT-247',
							'zCldMast-zOPT-248',
							'zCldMast-Moment Share Key= zShare-zPK-249',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-250',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb-251',
							'zCldMast-Originating Asset ID-252',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-253',
							'CMzCldMastMedData-zENT-254',
							'CMzCldMastMedData-CldMast= zCldMast-zPK-255',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-256',
							'AAAzCldMastMedData-zENT-257',
							'AAAzCldMastMedData-CldMast key-258',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-259',
							'zExtAttr-zPK= zAsset-zExtendedAttributes-260',
							'zExtAttr-zENT-261',
							'zExtAttr-zOPT-262',
							'zExtAttr-Asset Key-263',
							'zIntResou-zPK-264',
							'zIntResou-zENT-265',
							'zIntResou-zOPT-266',
							'zIntResou-Asset= zAsset_zPK-267',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-268',
							'zMedAnlyAstAttr-zEnt-269',
							'zMedAnlyAstAttr-zOpt-270',
							'zMedAnlyAstAttr-Asset= zAsset-zPK-271')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 16 PhotoData-Photos.sqlite')

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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG-THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG-HEIC-quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj-Mutation_Data-37'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		CASE zAsset.ZDELETEREASON
			WHEN 1 THEN '1-StillTesting Delete-Reason-1'
			WHEN 2 THEN '2-StillTesting Delete-Reason-2'
			WHEN 3 THEN '3-StillTesting Delete-Reason-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
		END AS 'zAsset-Delete-Reason',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[268], row[269], row[270], row[271], row[272], row[273]))

				counter += 1

			description = 'Parses iOS 17 asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE' \
' and other tables. This and other related parsers should provide data for investigative' \
' analysis of assets being stored locally on the device verses assets being stored in' \
' iCloud Photos as the result of optimization. This is very large query and script,' \
' I recommend opening the TSV generated report with Zimmermans Tools' \
' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Asset_IntResou-Optimization')
			report.start_artifact_report(report_folder, 'Ph50.1-Asset_IntResou-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
							'zIntResou-Local Availability-4QueryStart-1',
							'zIntResou-Remote Availability-4QueryStart-2',
							'zIntResou-Resource Type-4QueryStart-3',
							'zIntResou-Datastore Sub-Type-4QueryStart-4',
							'zIntResou-Recipe ID-4QueryStart-5',
							'zAsset Complete-6',
							'zAsset-zPK-7',
							'zAddAssetAttr-zPK-8',
							'zAsset-UUID = store.cloudphotodb-9',
							'zAddAssetAttr-Master Fingerprint-10',
							'zIntResou-Fingerprint-11',
							'zAsset-Bundle Scope-12',
							'zAsset-Syndication State-13',
							'zAsset-Cloud is My Asset-14',
							'zAsset-Cloud is deletable-Asset-15',
							'zAsset-Cloud_Local_State-16',
							'zAsset-Visibility State-17',
							'zExtAttr-Camera Make-18',
							'zExtAttr-Camera Model-19',
							'zExtAttr-Lens Model-20',
							'zExtAttr-Flash Fired-21',
							'zExtAttr-Focal Lenght-22',
							'zExtAttr-Focal Lenth in 35MM-23',
							'zExtAttr-Digital Zoom Ratio-24',
							'zAsset-Derived Camera Capture Device-25',
							'zAddAssetAttr-Camera Captured Device-26',
							'zAddAssetAttr-Imported by-27',
							'zCldMast-Imported By-28',
							'zAddAssetAttr.Imported by Bundle Identifier-29',
							'zAddAssetAttr-Imported By Display Name-30',
							'zCldMast-Imported by Bundle ID-31',
							'zCldMast-Imported by Display Name-32',
							'zAsset-Saved Asset Type-33',
							'zAsset-Directory-Path-34',
							'zAsset-Filename-35',
							'zAddAssetAttr- Original Filename-36',
							'zCldMast- Original Filename-37',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-38',
							'zAsset-Active Library Scope Participation State-39',
							'zAsset-Library Scope Share State- StillTesting-40',
							'zAsset-Added Date-41',
							'zAsset- SortToken -CameraRoll-42',
							'zAddAssetAttr-Date Created Source-43',
							'zAsset-Date Created-44',
							'zCldMast-Creation Date-45',
							'zIntResou-CldMst Date Created-46',
							'zAddAssetAttr-Time Zone Name-47',
							'zAddAssetAttr-Time Zone Offset-48',
							'zAddAssetAttr-Inferred Time Zone Offset-49',
							'zAddAssetAttr-EXIF-String-50',
							'zAsset-Modification Date-51',
							'zAsset-Last Shared Date-52',
							'zCldMast-Cloud Local State-53',
							'zCldMast-Import Date-54',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-55',
							'zAddAssetAttr-Import Session ID-56',
							'zAddAssetAttr-Alt Import Image Date-57',
							'zCldMast-Import Session ID- AirDrop-StillTesting-58',
							'zAsset-Cloud Batch Publish Date-59',
							'zAsset-Cloud Server Publish Date-60',
							'zAsset-Cloud Download Requests-61',
							'zAsset-Cloud Batch ID-62',
							'zAddAssetAttr-Upload Attempts-63',
							'zAsset-Latitude-64',
							'zExtAttr-Latitude-65',
							'zAsset-Longitude-66',
							'zExtAttr-Longitude-67',
							'zAddAssetAttr-GPS Horizontal Accuracy-68',
							'zAddAssetAttr-Location Hash-69',
							'zAddAssetAttr-Shifted Location Valid-70',
							'zAddAssetAttr-Shifted Location Data-71',
							'zAddAssetAttr-Reverse Location Is Valid-72',
							'zAddAssetAttr-Reverse Location Data-73',
							'AAAzCldMastMedData-zOPT-74',
							'zAddAssetAttr-Media Metadata Type-75',
							'AAAzCldMastMedData-Data-76',
							'CldMasterzCldMastMedData-zOPT-77',
							'zCldMast-Media Metadata Type-78',
							'CMzCldMastMedData-Data-79',
							'zAsset-Search Index Rebuild State-80',
							'zAddAssetAttr-Syndication History-81',
							'zMedAnlyAstAttr-Syndication Processing Version-82',
							'zMedAnlyAstAttr-Syndication Processing Value-83',
							'zAsset-Orientation-84',
							'zAddAssetAttr-Original Orientation-85',
							'zAsset-Kind-86',
							'zAsset-Kind-Sub-Type-87',
							'zAddAssetAttr-Cloud Kind Sub Type-88',
							'zAsset-Playback Style-89',
							'zAsset-Playback Variation-90',
							'zAsset-Video Duration-91',
							'zExtAttr-Duration-92',
							'zAsset-Video CP Duration-93',
							'zAddAssetAttr-Video CP Duration Time Scale-94',
							'zAsset-Video CP Visibility State-95',
							'zAddAssetAttr-Video CP Display Value-96',
							'zAddAssetAttr-Video CP Display Time Scale-97',
							'zIntResou-Datastore Class ID-98',
							'zAsset-Cloud Placeholder Kind-99',
							'zIntResou-Local Availability-100',
							'zIntResou-Local Availability Target-101',
							'zIntResou-Cloud Local State-102',
							'zIntResou-Remote Availability-103',
							'zIntResou-Remote Availability Target-104',
							'zIntResou-Transient Cloud Master-105',
							'zIntResou-Side Car Index-106',
							'zIntResou- File ID-107',
							'zIntResou-Version-108',
							'zAddAssetAttr- Original-File-Size-109',
							'zIntResou-Resource Type-110',
							'zIntResou-Datastore Sub-Type-111',
							'zIntResou-Cloud Source Type-112',
							'zIntResou-Data Length-113',
							'zIntResou-Recipe ID-114',
							'zIntResou-Cloud Last Prefetch Date-115',
							'zIntResou-Cloud Prefetch Count-116',
							'zIntResou- Cloud-Last-OnDemand Download-Date-117',
							'zIntResou-UniformTypeID_UTI_Conformance_Hint-118',
							'zIntResou-Compact-UTI-119',
							'zAsset-Uniform Type ID-120',
							'zAsset-Original Color Space-121',
							'zCldMast-Uniform_Type_ID-122',
							'zCldMast-Full Size JPEG Source-123',
							'zAsset-HDR Gain-124',
							'zAsset-zHDR_Type-125',
							'zExtAttr-Codec-126',
							'zIntResou-Codec Four Char Code Name-127',
							'zCldMast-Codec Name-128',
							'zCldMast-Video Frame Rate-129',
							'zCldMast-Placeholder State-130',
							'zAsset-Depth_Type-131',
							'zAsset-Avalanche UUID-132',
							'zAsset-Avalanche_Pick_Type-BurstAsset-133',
							'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-134',
							'zAddAssetAttr-Cloud Recovery State-135',
							'zAddAssetAttr-Cloud State Recovery Attempts Count-136',
							'zAsset-Deferred Processing Needed-137',
							'zAsset-Video Deferred Processing Needed-138',
							'zAddAssetAttr-Deferred Photo Identifier-139',
							'zAddAssetAttr-Deferred Processing Candidate Options-140',
							'zAsset-Has Adjustments-Camera-Effects-Filters-141',
							'zAsset-Adjustment Timestamp-142',
							'zAddAssetAttr-Editor Bundle ID-143',
							'zAddAssetAttr-Montage-144',
							'zAsset-Favorite-145',
							'zAsset-Hidden-146',
							'zAsset-Trashed State-LocalAssetRecentlyDeleted-147',
							'zAsset-Trashed Date-148',
							'zAsset-Trashed by Participant= zSharePartic_zPK-149',
							'zAsset-Delete-Reason-150',
							'zIntResou-Trash State-151',
							'zIntResou-Trashed Date-152',
							'zAsset-Cloud Delete State-153',
							'zIntResou-Cloud Delete State-154',
							'zAddAssetAttr-PTP Trashed State-155',
							'zIntResou-PTP Trashed State-156',
							'zIntResou-Cloud Delete Asset UUID With Resource Type-157',
							'zMedAnlyAstAttr-Media Analysis Timestamp-158',
							'zAsset-Analysis State Modificaion Date-159',
							'zAddAssetAttr- Pending View Count-160',
							'zAddAssetAttr- View Count-161',
							'zAddAssetAttr- Pending Play Count-162',
							'zAddAssetAttr- Play Count-163',
							'zAddAssetAttr- Pending Share Count-164',
							'zAddAssetAttr- Share Count-165',
							'zAddAssetAttr-Allowed for Analysis-166',
							'zAddAssetAttr-Scene Analysis Version-167',
							'zAddAssetAttr-Scene Analysis is From Preview-168',
							'zAddAssetAttr-Scene Analysis Timestamp-169',
							'zAsset-Duplication Asset Visibility State-170',
							'zAddAssetAttr-Destination Asset Copy State-171',
							'zAddAssetAttr-Duplicate Detector Perceptual Processing State-172',
							'zAddAssetAttr-Source Asset for Duplication Scope ID-173',
							'zCldMast-Source Master For Duplication Scope ID-174',
							'zAddAssetAttr-Source Asset For Duplication ID-175',
							'zCldMast-Source Master for Duplication ID-176',
							'zAddAssetAttr-Variation Suggestions States-177',
							'zAsset-High Frame Rate State-178',
							'zAsset-Video Key Frame Time Scale-179',
							'zAsset-Video Key Frame Value-180',
							'zExtAttr-ISO-181',
							'zExtAttr-Metering Mode-182',
							'zExtAttr-Sample Rate-183',
							'zExtAttr-Track Format-184',
							'zExtAttr-White Balance-185',
							'zExtAttr-Aperture-186',
							'zExtAttr-BitRate-187',
							'zExtAttr-Exposure Bias-188',
							'zExtAttr-Frames Per Second-189',
							'zExtAttr-Shutter Speed-190',
							'zExtAttr-Slush Scene Bias-191',
							'zExtAttr-Slush Version-192',
							'zExtAttr-Slush Preset-193',
							'zExtAttr-Slush Warm Bias-194',
							'zAsset-Height-195',
							'zAddAssetAttr-Original Height-196',
							'zIntResou-Unoriented Height-197',
							'zAsset-Width-198',
							'zAddAssetAttr-Original Width-199',
							'zIntResou-Unoriented Width-200',
							'zAsset-Thumbnail Index-201',
							'zAddAssetAttr-Embedded Thumbnail Height-202',
							'zAddAssetAttr-Embedded Thumbnail Length-203',
							'zAddAssetAttr-Embedded Thumbnail Offset-204',
							'zAddAssetAttr-Embedded Thumbnail Width-205',
							'zAsset-Packed Acceptable Crop Rect-206',
							'zAsset-Packed Badge Attributes-207',
							'zAsset-Packed Preferred Crop Rect-208',
							'zAsset-Curation Score-209',
							'zAsset-Camera Processing Adjustment State-210',
							'zAsset-Depth Type-211',
							'zAsset-Is Magic Carpet-QuicktimeMOVfile-212',
							'zAddAssetAttr-Orig Resource Choice-213',
							'zAsset-Spatial Type-214',
							'zAddAssetAttr-Spatial Over Capture Group ID-215',
							'zAddAssetAttr-Place Annotation Data-216',
							'zAddAssetAttr-Distance Identity-HEX-217',
							'zAddAssetAttr-Edited IPTC Attributes-218',
							'zAddAssetAttr-Title-Comments via Cloud Website-219',
							'zAddAssetAttr-Accessibility Description-220',
							'zAddAssetAttr-Photo Stream Tag ID-221',
							'zAddAssetAttr-Share Type-222',
							'zAddAssetAttr-Library Scope Asset Contributors To Update-223',
							'zAsset-Overall Aesthetic Score-224',
							'zAsset-zENT-225',
							'zAsset-zOPT-226',
							'zAsset-Master= zCldMast-zPK-227',
							'zAsset-Extended Attributes= zExtAttr-zPK-228',
							'zAsset-Import Session Key-229',
							'zAsset-Photo Analysis Attributes Key-230',
							'zAsset-FOK-Cloud Feed Asset Entry Key-231',
							'zAsset-Computed Attributes Asset Key-232',
							'zAsset-Promotion Score-233',
							'zAsset-Iconic Score-234',
							'zAsset-Media Analysis Attributes Key-235',
							'zAsset-Media Group UUID-236',
							'zAsset-Cloud_Asset_GUID = store.cloudphotodb-237',
							'zAsset.Cloud Collection GUID-238',
							'zAddAssetAttr-zENT-239',
							'ZAddAssetAttr-zOPT-240',
							'zAddAssetAttr-zAsset= zAsset_zPK-241',
							'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-242',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-243',
							'zAddAssetAttr-Public Global UUID-244',
							'zAddAssetAttr-Original Assets UUID-245',
							'zAddAssetAttr-Originating Asset Identifier-246',
							'zAddAssetAttr.Adjusted Fingerprint-247',
							'zCldMast-zPK= zAsset-Master-248',
							'zCldMast-zENT-249',
							'zCldMast-zOPT-250',
							'zCldMast-Moment Share Key= zShare-zPK-251',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-252',
							'zCldMast-Cloud_Master_GUID = store.cloudphotodb-253',
							'zCldMast-Originating Asset ID-254',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-255',
							'CMzCldMastMedData-zENT-256',
							'CMzCldMastMedData-CldMast= zCldMast-zPK-257',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-258',
							'AAAzCldMastMedData-zENT-259',
							'AAAzCldMastMedData-CldMast key-260',
							'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-261',
							'zExtAttr-zPK= zAsset-zExtendedAttributes-262',
							'zExtAttr-zENT-263',
							'zExtAttr-zOPT-264',
							'zExtAttr-Asset Key-265',
							'zIntResou-zPK-266',
							'zIntResou-zENT-267',
							'zIntResou-zOPT-268',
							'zIntResou-Asset= zAsset_zPK-269',
							'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-270',
							'zMedAnlyAstAttr-zEnt-271',
							'zMedAnlyAstAttr-zOpt-272',
							'zMedAnlyAstAttr-Asset= zAsset-zPK-273')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph50.1-Asset_IntResou-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph50.1-Asset_IntResou-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No Internal Resource data available for iOS 17 PhotoData-Photos.sqlite')

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
	if version.parse(iosversion) <= version.parse("13.7"):
		logfunc("Unsupported version for SyndicationPL-Photos.sqlite ZINTERNALRESOURCE table data from iOS " + iosversion)
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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
		CASE zAsset.ZORIENTATION
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[236], row[237], row[238]))

				counter += 1

			description = 'Parses iOS 14 asset records from Syndication.photos.library-database-Photos.sqlite' \
' ZINTERNALRESOURCE and other tables. This and other related parsers should provide' \
' data for investigative analysis of assets being stored locally on the device verses' \
' assets being stored in iCloud Photos as the result of optimization. This is very' \
' large query and script, I recommend opening the TSV generated report with Zimmermans Tools' \
' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
			report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
						'zIntResou-Local Availability-4QueryStart-1',
						'zIntResou-Remote Availability-4QueryStart-2',
						'zIntResou-Resource Type-4QueryStart-3',
						'zIntResou-Datastore Sub-Type-4QueryStart-4',
						'zIntResou-Recipe ID-4QueryStart-5',
						'zAsset Complete-6',
						'zAsset-zPK-7',
						'zAddAssetAttr-zPK-8',
						'zAsset-UUID = store.cloudphotodb-9',
						'zAddAssetAttr-Master Fingerprint-10',
						'zIntResou-Fingerprint-11',
						'zAsset-Cloud is My Asset-12',
						'zAsset-Cloud is deletable-Asset-13',
						'zAsset-Cloud_Local_State-14',
						'zAsset-Visibility State-15',
						'zExtAttr-Camera Make-16',
						'zExtAttr-Camera Model-17',
						'zExtAttr-Lens Model-18',
						'zExtAttr-Flash Fired-19',
						'zExtAttr-Focal Lenght-20',
						'zAsset-Derived Camera Capture Device-21',
						'zAddAssetAttr-Camera Captured Device-22',
						'zAddAssetAttr-Imported by-23',
						'zCldMast-Imported By-24',
						'zAddAssetAttr-Creator Bundle ID-25',
						'zAddAssetAttr-Imported By Display Name-26',
						'zCldMast-Imported by Bundle ID-27',
						'zCldMast-Imported by Display Name-28',
						'zAsset-Saved Asset Type-29',
						'zAsset-Directory-Path-30',
						'zAsset-Filename-31',
						'zAddAssetAttr- Original Filename-32',
						'zCldMast- Original Filename-33',
						'zAsset-Added Date-34',
						'zAsset- SortToken -CameraRoll-35',
						'zAsset-Date Created-36',
						'zCldMast-Creation Date-37',
						'zIntResou-CldMst Date Created-38',
						'zAddAssetAttr-Time Zone Name-39',
						'zAddAssetAttr-Time Zone Offset-40',
						'zAddAssetAttr-Inferred Time Zone Offset-41',
						'zAddAssetAttr-EXIF-String-42',
						'zAsset-Modification Date-43',
						'zAsset-Last Shared Date-44',
						'zCldMast-Cloud Local State-45',
						'zCldMast-Import Date-46',
						'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-47',
						'zAddAssetAttr-Import Session ID-48',
						'zAddAssetAttr-Alt Import Image Date-49',
						'zCldMast-Import Session ID- AirDrop-StillTesting-50',
						'zAsset-Cloud Batch Publish Date-51',
						'zAsset-Cloud Server Publish Date-52',
						'zAsset-Cloud Download Requests-53',
						'zAsset-Cloud Batch ID-54',
						'zAddAssetAttr-Upload Attempts-55',
						'zAsset-Latitude-56',
						'zExtAttr-Latitude-57',
						'zAsset-Longitude-58',
						'zExtAttr-Longitude-59',
						'zAddAssetAttr-GPS Horizontal Accuracy-60',
						'zAddAssetAttr-Location Hash-61',
						'zAddAssetAttr-Shifted Location Valid-62',
						'zAddAssetAttr-Shifted Location Data-63',
						'zAddAssetAttr-Reverse Location Is Valid-64',
						'zAddAssetAttr-Reverse Location Data-65',
						'AAAzCldMastMedData-zOPT-66',
						'zAddAssetAttr-Media Metadata Type-67',
						'AAAzCldMastMedData-Data-68',
						'CldMasterzCldMastMedData-zOPT-69',
						'zCldMast-Media Metadata Type-70',
						'CMzCldMastMedData-Data-71',
						'zAsset-Orientation-72',
						'zAddAssetAttr-Original Orientation-73',
						'zAsset-Kind-74',
						'zAsset-Kind-Sub-Type-75',
						'zAddAssetAttr-Cloud Kind Sub Type-76',
						'zAsset-Playback Style-77',
						'zAsset-Playback Variation-78',
						'zAsset-Video Duration-79',
						'zExtAttr-Duration-80',
						'zAsset-Video CP Duration-81',
						'zAddAssetAttr-Video CP Duration Time Scale-82',
						'zAsset-Video CP Visibility State-83',
						'zAddAssetAttr-Video CP Display Value-84',
						'zAddAssetAttr-Video CP Display Time Scale-85',
						'zIntResou-Datastore Class ID-86',
						'zAsset-Cloud Placeholder Kind-87',
						'zIntResou-Local Availability-88',
						'zIntResou-Local Availability Target-89',
						'zIntResou-Cloud Local State-90',
						'zIntResou-Remote Availability-91',
						'zIntResou-Remote Availability Target-92',
						'zIntResou-Transient Cloud Master-93',
						'zIntResou-Side Car Index-94',
						'zIntResou- File ID-95',
						'zIntResou-Version-96',
						'zAddAssetAttr- Original-File-Size-97',
						'zIntResou-Resource Type-98',
						'zIntResou-Datastore Sub-Type-99',
						'zIntResou-Cloud Source Type-100',
						'zIntResou-Data Length-101',
						'zIntResou-Recipe ID-102',
						'zIntResou-Cloud Last Prefetch Date-103',
						'zIntResou-Cloud Prefetch Count-104',
						'zIntResou- Cloud-Last-OnDemand Download-Date-105',
						'zAsset-Uniform Type ID-106',
						'zAsset-Original Color Space-107',
						'zCldMast-Uniform_Type_ID-108',
						'zCldMast-Full Size JPEG Source-109',
						'zAsset-HDR Gain-110',
						'zExtAttr-Codec-111',
						'zCldMast-Codec Name-112',
						'zCldMast-Video Frame Rate-113',
						'zCldMast-Placeholder State-114',
						'zAsset-Depth_Type-115',
						'zAsset-Avalanche UUID-116',
						'zAsset-Avalanche_Pick_Type-BurstAsset-117',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-118',
						'zAddAssetAttr-Cloud Recovery State-119',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-120',
						'zAsset-Deferred Processing Needed-121',
						'zAddAssetAttr-Deferred Photo Identifier-122',
						'zAddAssetAttr-Deferred Processing Candidate Options-123',
						'zAsset-Has Adjustments-Camera-Effects-Filters-124',
						'zAsset-Adjustment Timestamp-125',
						'zAddAssetAttr-Editor Bundle ID-126',
						'zAddAssetAttr-Montage-127',
						'zAsset-Favorite-128',
						'zAsset-Hidden-129',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-130',
						'zAsset-Trashed Date-131',
						'zIntResou-Trash State-132',
						'zIntResou-Trashed Date-133',
						'zAsset-Cloud Delete State-134',
						'zIntResou-Cloud Delete State-135',
						'zAddAssetAttr-PTP Trashed State-136',
						'zIntResou-PTP Trashed State-137',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-138',
						'zMedAnlyAstAttr-Media Analysis Timestamp-139',
						'zAsset-Analysis State Modificaion Date-140',
						'zAddAssetAttr- Pending View Count-141',
						'zAddAssetAttr- View Count-142',
						'zAddAssetAttr- Pending Play Count-143',
						'zAddAssetAttr- Play Count-144',
						'zAddAssetAttr- Pending Share Count-145',
						'zAddAssetAttr- Share Count-146',
						'zAddAssetAttr-Allowed for Analysis-147',
						'zAddAssetAttr-Scene Analysis Version-148',
						'zAddAssetAttr-Scene Analysis Timestamp-149',
						'zAddAssetAttr-Destination Asset Copy State-150',
						'zAddAssetAttr-Variation Suggestions States-151',
						'zAsset-High Frame Rate State-152',
						'zAsset-Video Key Frame Time Scale-153',
						'zAsset-Video Key Frame Value-154',
						'zExtAttr-ISO-155',
						'zExtAttr-Metering Mode-156',
						'zExtAttr-Sample Rate-157',
						'zExtAttr-Track Format-158',
						'zExtAttr-White Balance-159',
						'zExtAttr-Aperture-160',
						'zExtAttr-BitRate-161',
						'zExtAttr-Exposure Bias-162',
						'zExtAttr-Frames Per Second-163',
						'zExtAttr-Shutter Speed-164',
						'zAsset-Height-165',
						'zAddAssetAttr-Original Height-166',
						'zIntResou-Unoriented Height-167',
						'zAsset-Width-168',
						'zAddAssetAttr-Original Width-169',
						'zIntResou-Unoriented Width-170',
						'zAsset-Thumbnail Index-171',
						'zAddAssetAttr-Embedded Thumbnail Height-172',
						'zAddAssetAttr-Embedded Thumbnail Length-173',
						'zAddAssetAttr-Embedded Thumbnail Offset-174',
						'zAddAssetAttr-Embedded Thumbnail Width-175',
						'zAsset-Packed Acceptable Crop Rect-176',
						'zAsset-Packed Badge Attributes-177',
						'zAsset-Packed Preferred Crop Rect-178',
						'zAsset-Curation Score-179',
						'zAsset-Camera Processing Adjustment State-180',
						'zAsset-Depth Type-181',
						'zAddAssetAttr-Orig Resource Choice-182',
						'zAddAssetAttr-Spatial Over Capture Group ID-183',
						'zAddAssetAttr-Place Annotation Data-184',
						'zAddAssetAttr-Distance Identity-HEX-185',
						'zAddAssetAttr-Edited IPTC Attributes-186',
						'zAddAssetAttr-Title-Comments via Cloud Website-187',
						'zAddAssetAttr-Accessibility Description-188',
						'zAddAssetAttr-Photo Stream Tag ID-189',
						'zAddAssetAttr-Share Type-190',
						'zAsset-Overall Aesthetic Score-191',
						'zAsset-zENT-192',
						'zAsset-zOPT-193',
						'zAsset-Master= zCldMast-zPK-194',
						'zAsset-Extended Attributes= zExtAttr-zPK-195',
						'zAsset-Import Session Key-196',
						'zAsset-FOK-Cloud Feed Asset Entry Key-197',
						'zAsset-Computed Attributes Asset Key-198',
						'zAsset-Promotion Score-199',
						'zAsset-Media Analysis Attributes Key-200',
						'zAsset-Media Group UUID-201',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-202',
						'zAsset.Cloud Collection GUID-203',
						'zAddAssetAttr-zENT-204',
						'ZAddAssetAttr-zOPT-205',
						'zAddAssetAttr-zAsset= zAsset_zPK-206',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-207',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-208',
						'zAddAssetAttr-Public Global UUID-209',
						'zAddAssetAttr-Original Assets UUID-210',
						'zAddAssetAttr-Originating Asset Identifier-211',
						'zAddAssetAttr.Adjusted Fingerprint-212',
						'zCldMast-zPK= zAsset-Master-213',
						'zCldMast-zENT-214',
						'zCldMast-zOPT-215',
						'zCldMast-Moment Share Key= zShare-zPK-216',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-217',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-218',
						'zCldMast-Originating Asset ID-219',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-220',
						'CMzCldMastMedData-zENT-221',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-222',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-223',
						'AAAzCldMastMedData-zENT-224',
						'AAAzCldMastMedData-CldMast key-225',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-226',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-227',
						'zExtAttr-zENT-228',
						'zExtAttr-zOPT-229',
						'zExtAttr-Asset Key-230',
						'zIntResou-zPK-231',
						'zIntResou-zENT-232',
						'zIntResou-zOPT-233',
						'zIntResou-Asset= zAsset_zPK-234',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-235',
						'zMedAnlyAstAttr-zEnt-236',
						'zMedAnlyAstAttr-zOpt-237',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-238')
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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG-THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG-HEIC-quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj-Mutation_Data-37'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[252], row[253], row[254], row[255], row[256], row[257], row[258], row[259],
								row[260], row[261], row[262]))

				counter += 1

			description = 'Parses iOS 15 asset records from Syndication.photos.library-database-Photos.sqlite' \
' ZINTERNALRESOURCE and other tables. This and other related parsers should provide' \
' data for investigative analysis of assets being stored locally on the device verses' \
' assets being stored in iCloud Photos as the result of optimization. This is very large' \
' query and script, I recommend opening the TSV generated report with Zimmermans Tools' \
' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
			report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
						'zIntResou-Local Availability-4QueryStart-1',
						'zIntResou-Remote Availability-4QueryStart-2',
						'zIntResou-Resource Type-4QueryStart-3',
						'zIntResou-Datastore Sub-Type-4QueryStart-4',
						'zIntResou-Recipe ID-4QueryStart-5',
						'zAsset Complete-6',
						'zAsset-zPK-7',
						'zAddAssetAttr-zPK-8',
						'zAsset-UUID = store.cloudphotodb-9',
						'zAddAssetAttr-Master Fingerprint-10',
						'zIntResou-Fingerprint-11',
						'zAsset-Bundle Scope-12',
						'zAsset-Syndication State-13',
						'zAsset-Cloud is My Asset-14',
						'zAsset-Cloud is deletable-Asset-15',
						'zAsset-Cloud_Local_State-16',
						'zAsset-Visibility State-17',
						'zExtAttr-Camera Make-18',
						'zExtAttr-Camera Model-19',
						'zExtAttr-Lens Model-20',
						'zExtAttr-Flash Fired-21',
						'zExtAttr-Focal Lenght-22',
						'zExtAttr-Focal Lenth in 35MM-23',
						'zExtAttr-Digital Zoom Ratio-24',
						'zAsset-Derived Camera Capture Device-25',
						'zAddAssetAttr-Camera Captured Device-26',
						'zAddAssetAttr-Imported by-27',
						'zCldMast-Imported By-28',
						'zAddAssetAttr.Imported by Bundle Identifier-29',
						'zAddAssetAttr-Imported By Display Name-30',
						'zCldMast-Imported by Bundle ID-31',
						'zCldMast-Imported by Display Name-32',
						'zAsset-Saved Asset Type-33',
						'zAsset-Directory-Path-34',
						'zAsset-Filename-35',
						'zAddAssetAttr- Original Filename-36',
						'zCldMast- Original Filename-37',
						'zAddAssetAttr- Syndication Identifier-SWY-Files-38',
						'zAsset-Added Date-39',
						'zAsset- SortToken -CameraRoll-40',
						'zAddAssetAttr-Date Created Source-41',
						'zAsset-Date Created-42',
						'zCldMast-Creation Date-43',
						'zIntResou-CldMst Date Created-44',
						'zAddAssetAttr-Time Zone Name-45',
						'zAddAssetAttr-Time Zone Offset-46',
						'zAddAssetAttr-Inferred Time Zone Offset-47',
						'zAddAssetAttr-EXIF-String-48',
						'zAsset-Modification Date-49',
						'zAsset-Last Shared Date-50',
						'zCldMast-Cloud Local State-51',
						'zCldMast-Import Date-52',
						'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-53',
						'zAddAssetAttr-Import Session ID-54',
						'zAddAssetAttr-Alt Import Image Date-55',
						'zCldMast-Import Session ID- AirDrop-StillTesting-56',
						'zAsset-Cloud Batch Publish Date-57',
						'zAsset-Cloud Server Publish Date-58',
						'zAsset-Cloud Download Requests-59',
						'zAsset-Cloud Batch ID-60',
						'zAddAssetAttr-Upload Attempts-61',
						'zAsset-Latitude-62',
						'zExtAttr-Latitude-63',
						'zAsset-Longitude-64',
						'zExtAttr-Longitude-65',
						'zAddAssetAttr-GPS Horizontal Accuracy-66',
						'zAddAssetAttr-Location Hash-67',
						'zAddAssetAttr-Shifted Location Valid-68',
						'zAddAssetAttr-Shifted Location Data-69',
						'zAddAssetAttr-Reverse Location Is Valid-70',
						'zAddAssetAttr-Reverse Location Data-71',
						'AAAzCldMastMedData-zOPT-72',
						'zAddAssetAttr-Media Metadata Type-73',
						'AAAzCldMastMedData-Data-74',
						'CldMasterzCldMastMedData-zOPT-75',
						'zCldMast-Media Metadata Type-76',
						'CMzCldMastMedData-Data-77',
						'zAddAssetAttr-Syndication History-78',
						'zMedAnlyAstAttr-Syndication Processing Version-79',
						'zMedAnlyAstAttr-Syndication Processing Value-80',
						'zAsset-Orientation-81',
						'zAddAssetAttr-Original Orientation-82',
						'zAsset-Kind-83',
						'zAsset-Kind-Sub-Type-84',
						'zAddAssetAttr-Cloud Kind Sub Type-85',
						'zAsset-Playback Style-86',
						'zAsset-Playback Variation-87',
						'zAsset-Video Duration-88',
						'zExtAttr-Duration-89',
						'zAsset-Video CP Duration-90',
						'zAddAssetAttr-Video CP Duration Time Scale-91',
						'zAsset-Video CP Visibility State-92',
						'zAddAssetAttr-Video CP Display Value-93',
						'zAddAssetAttr-Video CP Display Time Scale-94',
						'zIntResou-Datastore Class ID-95',
						'zAsset-Cloud Placeholder Kind-96',
						'zIntResou-Local Availability-97',
						'zIntResou-Local Availability Target-98',
						'zIntResou-Cloud Local State-99',
						'zIntResou-Remote Availability-100',
						'zIntResou-Remote Availability Target-101',
						'zIntResou-Transient Cloud Master-102',
						'zIntResou-Side Car Index-103',
						'zIntResou- File ID-104',
						'zIntResou-Version-105',
						'zAddAssetAttr- Original-File-Size-106',
						'zIntResou-Resource Type-107',
						'zIntResou-Datastore Sub-Type-108',
						'zIntResou-Cloud Source Type-109',
						'zIntResou-Data Length-110',
						'zIntResou-Recipe ID-111',
						'zIntResou-Cloud Last Prefetch Date-112',
						'zIntResou-Cloud Prefetch Count-113',
						'zIntResou- Cloud-Last-OnDemand Download-Date-114',
						'zIntResou-UniformTypeID_UTI_Conformance_Hint-115',
						'zIntResou-Compact-UTI-116',
						'zAsset-Uniform Type ID-117',
						'zAsset-Original Color Space-118',
						'zCldMast-Uniform_Type_ID-119',
						'zCldMast-Full Size JPEG Source-120',
						'zAsset-HDR Gain-121',
						'zAsset-zHDR_Type-122',
						'zExtAttr-Codec-123',
						'zIntResou-Codec Four Char Code Name-124',
						'zCldMast-Codec Name-125',
						'zCldMast-Video Frame Rate-126',
						'zCldMast-Placeholder State-127',
						'zAsset-Depth_Type-128',
						'zAsset-Avalanche UUID-129',
						'zAsset-Avalanche_Pick_Type-BurstAsset-130',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-131',
						'zAddAssetAttr-Cloud Recovery State-132',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-133',
						'zAsset-Deferred Processing Needed-134',
						'zAsset-Video Deferred Processing Needed-135',
						'zAddAssetAttr-Deferred Photo Identifier-136',
						'zAddAssetAttr-Deferred Processing Candidate Options-137',
						'zAsset-Has Adjustments-Camera-Effects-Filters-138',
						'zAsset-Adjustment Timestamp-139',
						'zAddAssetAttr-Editor Bundle ID-140',
						'zAddAssetAttr-Montage-141',
						'zAsset-Favorite-142',
						'zAsset-Hidden-143',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-144',
						'zAsset-Trashed Date-145',
						'zIntResou-Trash State-146',
						'zIntResou-Trashed Date-147',
						'zAsset-Cloud Delete State-148',
						'zIntResou-Cloud Delete State-149',
						'zAddAssetAttr-PTP Trashed State-150',
						'zIntResou-PTP Trashed State-151',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-152',
						'zMedAnlyAstAttr-Media Analysis Timestamp-153',
						'zAsset-Analysis State Modificaion Date-154',
						'zAddAssetAttr- Pending View Count-155',
						'zAddAssetAttr- View Count-156',
						'zAddAssetAttr- Pending Play Count-157',
						'zAddAssetAttr- Play Count-158',
						'zAddAssetAttr- Pending Share Count-159',
						'zAddAssetAttr- Share Count-160',
						'zAddAssetAttr-Allowed for Analysis-161',
						'zAddAssetAttr-Scene Analysis Version-162',
						'zAddAssetAttr-Scene Analysis is From Preview-163',
						'zAddAssetAttr-Scene Analysis Timestamp-164',
						'zAddAssetAttr-Destination Asset Copy State-165',
						'zAddAssetAttr-Source Asset for Duplication Scope ID-166',
						'zCldMast-Source Master For Duplication Scope ID-167',
						'zAddAssetAttr-Source Asset For Duplication ID-168',
						'zCldMast-Source Master for Duplication ID-169',
						'zAddAssetAttr-Variation Suggestions States-170',
						'zAsset-High Frame Rate State-171',
						'zAsset-Video Key Frame Time Scale-172',
						'zAsset-Video Key Frame Value-173',
						'zExtAttr-ISO-174',
						'zExtAttr-Metering Mode-175',
						'zExtAttr-Sample Rate-176',
						'zExtAttr-Track Format-177',
						'zExtAttr-White Balance-178',
						'zExtAttr-Aperture-179',
						'zExtAttr-BitRate-180',
						'zExtAttr-Exposure Bias-181',
						'zExtAttr-Frames Per Second-182',
						'zExtAttr-Shutter Speed-183',
						'zExtAttr-Slush Scene Bias-184',
						'zExtAttr-Slush Version-185',
						'zExtAttr-Slush Preset-186',
						'zExtAttr-Slush Warm Bias-187',
						'zAsset-Height-188',
						'zAddAssetAttr-Original Height-189',
						'zIntResou-Unoriented Height-190',
						'zAsset-Width-191',
						'zAddAssetAttr-Original Width-192',
						'zIntResou-Unoriented Width-193',
						'zAsset-Thumbnail Index-194',
						'zAddAssetAttr-Embedded Thumbnail Height-195',
						'zAddAssetAttr-Embedded Thumbnail Length-196',
						'zAddAssetAttr-Embedded Thumbnail Offset-197',
						'zAddAssetAttr-Embedded Thumbnail Width-198',
						'zAsset-Packed Acceptable Crop Rect-199',
						'zAsset-Packed Badge Attributes-200',
						'zAsset-Packed Preferred Crop Rect-201',
						'zAsset-Curation Score-202',
						'zAsset-Camera Processing Adjustment State-203',
						'zAsset-Depth Type-204',
						'zAsset-Is Magic Carpet-QuicktimeMOVfile-205',
						'zAddAssetAttr-Orig Resource Choice-206',
						'zAddAssetAttr-Spatial Over Capture Group ID-207',
						'zAddAssetAttr-Place Annotation Data-208',
						'zAddAssetAttr-Distance Identity-HEX-209',
						'zAddAssetAttr-Edited IPTC Attributes-210',
						'zAddAssetAttr-Title-Comments via Cloud Website-211',
						'zAddAssetAttr-Accessibility Description-212',
						'zAddAssetAttr-Photo Stream Tag ID-213',
						'zAddAssetAttr-Share Type-214',
						'zAsset-Overall Aesthetic Score-215',
						'zAsset-zENT-216',
						'zAsset-zOPT-217',
						'zAsset-Master= zCldMast-zPK-218',
						'zAsset-Extended Attributes= zExtAttr-zPK-219',
						'zAsset-Import Session Key-220',
						'zAsset-FOK-Cloud Feed Asset Entry Key-221',
						'zAsset-Computed Attributes Asset Key-222',
						'zAsset-Promotion Score-223',
						'zAsset-Media Analysis Attributes Key-224',
						'zAsset-Media Group UUID-225',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-226',
						'zAsset.Cloud Collection GUID-227',
						'zAddAssetAttr-zENT-228',
						'ZAddAssetAttr-zOPT-229',
						'zAddAssetAttr-zAsset= zAsset_zPK-230',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-231',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-232',
						'zAddAssetAttr-Public Global UUID-233',
						'zAddAssetAttr-Original Assets UUID-234',
						'zAddAssetAttr-Originating Asset Identifier-235',
						'zAddAssetAttr.Adjusted Fingerprint-236',
						'zCldMast-zPK= zAsset-Master-237',
						'zCldMast-zENT-238',
						'zCldMast-zOPT-239',
						'zCldMast-Moment Share Key= zShare-zPK-240',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-241',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-242',
						'zCldMast-Originating Asset ID-243',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-244',
						'CMzCldMastMedData-zENT-245',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-246',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-247',
						'AAAzCldMastMedData-zENT-248',
						'AAAzCldMastMedData-CldMast key-249',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-250',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-251',
						'zExtAttr-zENT-252',
						'zExtAttr-zOPT-253',
						'zExtAttr-Asset Key-254',
						'zIntResou-zPK-255',
						'zIntResou-zENT-256',
						'zIntResou-zOPT-257',
						'zIntResou-Asset= zAsset_zPK-258',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-259',
						'zMedAnlyAstAttr-zEnt-260',
						'zMedAnlyAstAttr-zOpt-261',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-262')
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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG-THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG-HEIC-quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj-Mutation_Data-37'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		CASE zAsset.ZDELETEREASON
			WHEN 1 THEN '1-StillTesting Delete-Reason-1'
			WHEN 2 THEN '2-StillTesting Delete-Reason-2'
			WHEN 3 THEN '3-StillTesting Delete-Reason-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
		END AS 'zAsset-Delete-Reason',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[260], row[261], row[262], row[263], row[264], row[265], row[266], row[267],
								row[268], row[269], row[270], row[271]))

				counter += 1

			description = 'Parses iOS 16 asset records from Syndication.photos.library-database-Photos.sqlite' \
' ZINTERNALRESOURCE and other tables. This and other related parsers should provide' \
' data for investigative analysis of assets being stored locally on the device verses' \
' assets being stored in iCloud Photos as the result of optimization. This is very large' \
' query and script, I recommend opening the TSV generated report with Zimmermans Tools' \
' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
' and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
			report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
						'zIntResou-Local Availability-4QueryStart-1',
						'zIntResou-Remote Availability-4QueryStart-2',
						'zIntResou-Resource Type-4QueryStart-3',
						'zIntResou-Datastore Sub-Type-4QueryStart-4',
						'zIntResou-Recipe ID-4QueryStart-5',
						'zAsset Complete-6',
						'zAsset-zPK-7',
						'zAddAssetAttr-zPK-8',
						'zAsset-UUID = store.cloudphotodb-9',
						'zAddAssetAttr-Master Fingerprint-10',
						'zIntResou-Fingerprint-11',
						'zAsset-Bundle Scope-12',
						'zAsset-Syndication State-13',
						'zAsset-Cloud is My Asset-14',
						'zAsset-Cloud is deletable-Asset-15',
						'zAsset-Cloud_Local_State-16',
						'zAsset-Visibility State-17',
						'zExtAttr-Camera Make-18',
						'zExtAttr-Camera Model-19',
						'zExtAttr-Lens Model-20',
						'zExtAttr-Flash Fired-21',
						'zExtAttr-Focal Lenght-22',
						'zExtAttr-Focal Lenth in 35MM-23',
						'zExtAttr-Digital Zoom Ratio-24',
						'zAsset-Derived Camera Capture Device-25',
						'zAddAssetAttr-Camera Captured Device-26',
						'zAddAssetAttr-Imported by-27',
						'zCldMast-Imported By-28',
						'zAddAssetAttr.Imported by Bundle Identifier-29',
						'zAddAssetAttr-Imported By Display Name-30',
						'zCldMast-Imported by Bundle ID-31',
						'zCldMast-Imported by Display Name-32',
						'zAsset-Saved Asset Type-33',
						'zAsset-Directory-Path-34',
						'zAsset-Filename-35',
						'zAddAssetAttr- Original Filename-36',
						'zCldMast- Original Filename-37',
						'zAddAssetAttr- Syndication Identifier-SWY-Files-38',
						'zAsset-Active Library Scope Participation State-39',
						'zAsset-Library Scope Share State- StillTesting-40',
						'zAsset-Added Date-41',
						'zAsset- SortToken -CameraRoll-42',
						'zAddAssetAttr-Date Created Source-43',
						'zAsset-Date Created-44',
						'zCldMast-Creation Date-45',
						'zIntResou-CldMst Date Created-46',
						'zAddAssetAttr-Time Zone Name-47',
						'zAddAssetAttr-Time Zone Offset-48',
						'zAddAssetAttr-Inferred Time Zone Offset-49',
						'zAddAssetAttr-EXIF-String-50',
						'zAsset-Modification Date-51',
						'zAsset-Last Shared Date-52',
						'zCldMast-Cloud Local State-53',
						'zCldMast-Import Date-54',
						'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-55',
						'zAddAssetAttr-Import Session ID-56',
						'zAddAssetAttr-Alt Import Image Date-57',
						'zCldMast-Import Session ID- AirDrop-StillTesting-58',
						'zAsset-Cloud Batch Publish Date-59',
						'zAsset-Cloud Server Publish Date-60',
						'zAsset-Cloud Download Requests-61',
						'zAsset-Cloud Batch ID-62',
						'zAddAssetAttr-Upload Attempts-63',
						'zAsset-Latitude-64',
						'zExtAttr-Latitude-65',
						'zAsset-Longitude-66',
						'zExtAttr-Longitude-67',
						'zAddAssetAttr-GPS Horizontal Accuracy-68',
						'zAddAssetAttr-Location Hash-69',
						'zAddAssetAttr-Shifted Location Valid-70',
						'zAddAssetAttr-Shifted Location Data-71',
						'zAddAssetAttr-Reverse Location Is Valid-72',
						'zAddAssetAttr-Reverse Location Data-73',
						'AAAzCldMastMedData-zOPT-74',
						'zAddAssetAttr-Media Metadata Type-75',
						'AAAzCldMastMedData-Data-76',
						'CldMasterzCldMastMedData-zOPT-77',
						'zCldMast-Media Metadata Type-78',
						'CMzCldMastMedData-Data-79',
						'zAsset-Search Index Rebuild State-80',
						'zAddAssetAttr-Syndication History-81',
						'zMedAnlyAstAttr-Syndication Processing Version-82',
						'zMedAnlyAstAttr-Syndication Processing Value-83',
						'zAsset-Orientation-84',
						'zAddAssetAttr-Original Orientation-85',
						'zAsset-Kind-86',
						'zAsset-Kind-Sub-Type-87',
						'zAddAssetAttr-Cloud Kind Sub Type-88',
						'zAsset-Playback Style-89',
						'zAsset-Playback Variation-90',
						'zAsset-Video Duration-91',
						'zExtAttr-Duration-92',
						'zAsset-Video CP Duration-93',
						'zAddAssetAttr-Video CP Duration Time Scale-94',
						'zAsset-Video CP Visibility State-95',
						'zAddAssetAttr-Video CP Display Value-96',
						'zAddAssetAttr-Video CP Display Time Scale-97',
						'zIntResou-Datastore Class ID-98',
						'zAsset-Cloud Placeholder Kind-99',
						'zIntResou-Local Availability-100',
						'zIntResou-Local Availability Target-101',
						'zIntResou-Cloud Local State-102',
						'zIntResou-Remote Availability-103',
						'zIntResou-Remote Availability Target-104',
						'zIntResou-Transient Cloud Master-105',
						'zIntResou-Side Car Index-106',
						'zIntResou- File ID-107',
						'zIntResou-Version-108',
						'zAddAssetAttr- Original-File-Size-109',
						'zIntResou-Resource Type-110',
						'zIntResou-Datastore Sub-Type-111',
						'zIntResou-Cloud Source Type-112',
						'zIntResou-Data Length-113',
						'zIntResou-Recipe ID-114',
						'zIntResou-Cloud Last Prefetch Date-115',
						'zIntResou-Cloud Prefetch Count-116',
						'zIntResou- Cloud-Last-OnDemand Download-Date-117',
						'zIntResou-UniformTypeID_UTI_Conformance_Hint-118',
						'zIntResou-Compact-UTI-119',
						'zAsset-Uniform Type ID-120',
						'zAsset-Original Color Space-121',
						'zCldMast-Uniform_Type_ID-122',
						'zCldMast-Full Size JPEG Source-123',
						'zAsset-HDR Gain-124',
						'zAsset-zHDR_Type-125',
						'zExtAttr-Codec-126',
						'zIntResou-Codec Four Char Code Name-127',
						'zCldMast-Codec Name-128',
						'zCldMast-Video Frame Rate-129',
						'zCldMast-Placeholder State-130',
						'zAsset-Depth_Type-131',
						'zAsset-Avalanche UUID-132',
						'zAsset-Avalanche_Pick_Type-BurstAsset-133',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-134',
						'zAddAssetAttr-Cloud Recovery State-135',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-136',
						'zAsset-Deferred Processing Needed-137',
						'zAsset-Video Deferred Processing Needed-138',
						'zAddAssetAttr-Deferred Photo Identifier-139',
						'zAddAssetAttr-Deferred Processing Candidate Options-140',
						'zAsset-Has Adjustments-Camera-Effects-Filters-141',
						'zAsset-Adjustment Timestamp-142',
						'zAddAssetAttr-Editor Bundle ID-143',
						'zAddAssetAttr-Montage-144',
						'zAsset-Favorite-145',
						'zAsset-Hidden-146',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-147',
						'zAsset-Trashed Date-148',
						'zAsset-Trashed by Participant= zSharePartic_zPK-149',
						'zAsset-Delete-Reason-150',
						'zIntResou-Trash State-151',
						'zIntResou-Trashed Date-152',
						'zAsset-Cloud Delete State-153',
						'zIntResou-Cloud Delete State-154',
						'zAddAssetAttr-PTP Trashed State-155',
						'zIntResou-PTP Trashed State-156',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-157',
						'zMedAnlyAstAttr-Media Analysis Timestamp-158',
						'zAsset-Analysis State Modificaion Date-159',
						'zAddAssetAttr- Pending View Count-160',
						'zAddAssetAttr- View Count-161',
						'zAddAssetAttr- Pending Play Count-162',
						'zAddAssetAttr- Play Count-163',
						'zAddAssetAttr- Pending Share Count-164',
						'zAddAssetAttr- Share Count-165',
						'zAddAssetAttr-Allowed for Analysis-166',
						'zAddAssetAttr-Scene Analysis Version-167',
						'zAddAssetAttr-Scene Analysis is From Preview-168',
						'zAddAssetAttr-Scene Analysis Timestamp-169',
						'zAsset-Duplication Asset Visibility State-170',
						'zAddAssetAttr-Destination Asset Copy State-171',
						'zAddAssetAttr-Duplicate Detector Perceptual Processing State-172',
						'zAddAssetAttr-Source Asset for Duplication Scope ID-173',
						'zCldMast-Source Master For Duplication Scope ID-174',
						'zAddAssetAttr-Source Asset For Duplication ID-175',
						'zCldMast-Source Master for Duplication ID-176',
						'zAddAssetAttr-Variation Suggestions States-177',
						'zAsset-High Frame Rate State-178',
						'zAsset-Video Key Frame Time Scale-179',
						'zAsset-Video Key Frame Value-180',
						'zExtAttr-ISO-181',
						'zExtAttr-Metering Mode-182',
						'zExtAttr-Sample Rate-183',
						'zExtAttr-Track Format-184',
						'zExtAttr-White Balance-185',
						'zExtAttr-Aperture-186',
						'zExtAttr-BitRate-187',
						'zExtAttr-Exposure Bias-188',
						'zExtAttr-Frames Per Second-189',
						'zExtAttr-Shutter Speed-190',
						'zExtAttr-Slush Scene Bias-191',
						'zExtAttr-Slush Version-192',
						'zExtAttr-Slush Preset-193',
						'zExtAttr-Slush Warm Bias-194',
						'zAsset-Height-195',
						'zAddAssetAttr-Original Height-196',
						'zIntResou-Unoriented Height-197',
						'zAsset-Width-198',
						'zAddAssetAttr-Original Width-199',
						'zIntResou-Unoriented Width-200',
						'zAsset-Thumbnail Index-201',
						'zAddAssetAttr-Embedded Thumbnail Height-202',
						'zAddAssetAttr-Embedded Thumbnail Length-203',
						'zAddAssetAttr-Embedded Thumbnail Offset-204',
						'zAddAssetAttr-Embedded Thumbnail Width-205',
						'zAsset-Packed Acceptable Crop Rect-206',
						'zAsset-Packed Badge Attributes-207',
						'zAsset-Packed Preferred Crop Rect-208',
						'zAsset-Curation Score-209',
						'zAsset-Camera Processing Adjustment State-210',
						'zAsset-Depth Type-211',
						'zAsset-Is Magic Carpet-QuicktimeMOVfile-212',
						'zAddAssetAttr-Orig Resource Choice-213',
						'zAddAssetAttr-Spatial Over Capture Group ID-214',
						'zAddAssetAttr-Place Annotation Data-215',
						'zAddAssetAttr-Distance Identity-HEX-216',
						'zAddAssetAttr-Edited IPTC Attributes-217',
						'zAddAssetAttr-Title-Comments via Cloud Website-218',
						'zAddAssetAttr-Accessibility Description-219',
						'zAddAssetAttr-Photo Stream Tag ID-220',
						'zAddAssetAttr-Share Type-221',
						'zAddAssetAttr-Library Scope Asset Contributors To Update-222',
						'zAsset-Overall Aesthetic Score-223',
						'zAsset-zENT-224',
						'zAsset-zOPT-225',
						'zAsset-Master= zCldMast-zPK-226',
						'zAsset-Extended Attributes= zExtAttr-zPK-227',
						'zAsset-Import Session Key-228',
						'zAsset-Photo Analysis Attributes Key-229',
						'zAsset-FOK-Cloud Feed Asset Entry Key-230',
						'zAsset-Computed Attributes Asset Key-231',
						'zAsset-Promotion Score-232',
						'zAsset-Media Analysis Attributes Key-233',
						'zAsset-Media Group UUID-234',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-235',
						'zAsset.Cloud Collection GUID-236',
						'zAddAssetAttr-zENT-237',
						'ZAddAssetAttr-zOPT-238',
						'zAddAssetAttr-zAsset= zAsset_zPK-239',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-240',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-241',
						'zAddAssetAttr-Public Global UUID-242',
						'zAddAssetAttr-Original Assets UUID-243',
						'zAddAssetAttr-Originating Asset Identifier-244',
						'zAddAssetAttr.Adjusted Fingerprint-245',
						'zCldMast-zPK= zAsset-Master-246',
						'zCldMast-zENT-247',
						'zCldMast-zOPT-248',
						'zCldMast-Moment Share Key= zShare-zPK-249',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-250',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-251',
						'zCldMast-Originating Asset ID-252',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-253',
						'CMzCldMastMedData-zENT-254',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-255',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-256',
						'AAAzCldMastMedData-zENT-257',
						'AAAzCldMastMedData-CldMast key-258',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-259',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-260',
						'zExtAttr-zENT-261',
						'zExtAttr-zOPT-262',
						'zExtAttr-Asset Key-263',
						'zIntResou-zPK-264',
						'zIntResou-zENT-265',
						'zIntResou-zOPT-266',
						'zIntResou-Asset= zAsset_zPK-267',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-268',
						'zMedAnlyAstAttr-zEnt-269',
						'zMedAnlyAstAttr-zOpt-270',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-271')
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
		END AS 'zAsset-Cloud is deletable-Asset',
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
			WHEN 0 THEN '0-Back-Camera-Other-0'
			WHEN 1 THEN '1-Front-Camera-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
		END AS 'zAsset-Derived Camera Capture Device',
		CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
			WHEN 0 THEN '0-Back-Camera-Other-0'
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 1 THEN '1-Video-Default-Adjustment-Horizontal-Camera-(left)-1'
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
			WHEN 3 THEN '3-JPG-Asset_Only_PhDa-Thumb-V2-3'
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
			WHEN 0 THEN '0-NA-Doesnt_Conform-0'
			WHEN 1 THEN '1-UTTypeImage-1'
			WHEN 2 THEN '2-UTTypeProRawPhoto-2'
			WHEN 3 THEN '3-UTTypeMovie-3'
			ELSE 'Unknown-New-Value!: ' || zIntResou.ZUTICONFORMANCEHINT || ''
		END AS 'zIntResou-UniformTypeID_UTI_Conformance_Hint',
		CASE zIntResou.ZCOMPACTUTI
			WHEN 1 THEN '1-JPEG-THM-1'
			WHEN 3 THEN '3-HEIC-3'
			WHEN 6 THEN '6-PNG-6'
			WHEN 7 THEN '7-StillTesting'
			WHEN 9 THEN '9-DNG-9'
			WHEN 23 THEN '23-JPEG-HEIC-quicktime-mov-23'
			WHEN 24 THEN '24-MPEG4-24'
			WHEN 36 THEN '36-Wallpaper-36'
			WHEN 37 THEN '37-Adj-Mutation_Data-37'
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
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
		END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
		CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
			WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
			WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
			WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
			WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
			WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
			WHEN 32 THEN '32-StillTesting-32_RT'
			WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
		END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
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
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
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
			WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
		END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
		DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		CASE zAsset.ZDELETEREASON
			WHEN 1 THEN '1-StillTesting Delete-Reason-1'
			WHEN 2 THEN '2-StillTesting Delete-Reason-2'
			WHEN 3 THEN '3-StillTesting Delete-Reason-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZDELETEREASON || ''
		END AS 'zAsset-Delete-Reason',
		CASE zIntResou.ZTRASHEDSTATE
			WHEN 0 THEN '0-zIntResou-Not In Trash-Recently Deleted-0'
			WHEN 1 THEN '1-zIntResou-In Trash-Recently Deleted-1'
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
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
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
								row[268], row[269], row[270], row[271], row[272], row[273]))

				counter += 1

			description = 'Parses iOS 17 asset records from Syndication.photos.library-database-Photos.sqlite' \
' ZINTERNALRESOURCE and and other tables. This and other related parsers should' \
' provide data for investigative analysis of assets being stored locally on the' \
' device verses assets being stored in iCloud Photos as the result of optimization.' \
' This is very large query and script, I recommend opening the TSV generated report' \
' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer' \
' to view, search, and filter the results.'
			report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
			report.start_artifact_report(report_folder, 'Ph50.2-Asset_IntResou-SyndPL', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-4QueryStart-0',
						'zIntResou-Local Availability-4QueryStart-1',
						'zIntResou-Remote Availability-4QueryStart-2',
						'zIntResou-Resource Type-4QueryStart-3',
						'zIntResou-Datastore Sub-Type-4QueryStart-4',
						'zIntResou-Recipe ID-4QueryStart-5',
						'zAsset Complete-6',
						'zAsset-zPK-7',
						'zAddAssetAttr-zPK-8',
						'zAsset-UUID = store.cloudphotodb-9',
						'zAddAssetAttr-Master Fingerprint-10',
						'zIntResou-Fingerprint-11',
						'zAsset-Bundle Scope-12',
						'zAsset-Syndication State-13',
						'zAsset-Cloud is My Asset-14',
						'zAsset-Cloud is deletable-Asset-15',
						'zAsset-Cloud_Local_State-16',
						'zAsset-Visibility State-17',
						'zExtAttr-Camera Make-18',
						'zExtAttr-Camera Model-19',
						'zExtAttr-Lens Model-20',
						'zExtAttr-Flash Fired-21',
						'zExtAttr-Focal Lenght-22',
						'zExtAttr-Focal Lenth in 35MM-23',
						'zExtAttr-Digital Zoom Ratio-24',
						'zAsset-Derived Camera Capture Device-25',
						'zAddAssetAttr-Camera Captured Device-26',
						'zAddAssetAttr-Imported by-27',
						'zCldMast-Imported By-28',
						'zAddAssetAttr.Imported by Bundle Identifier-29',
						'zAddAssetAttr-Imported By Display Name-30',
						'zCldMast-Imported by Bundle ID-31',
						'zCldMast-Imported by Display Name-32',
						'zAsset-Saved Asset Type-33',
						'zAsset-Directory-Path-34',
						'zAsset-Filename-35',
						'zAddAssetAttr- Original Filename-36',
						'zCldMast- Original Filename-37',
						'zAddAssetAttr- Syndication Identifier-SWY-Files-38',
						'zAsset-Active Library Scope Participation State-39',
						'zAsset-Library Scope Share State- StillTesting-40',
						'zAsset-Added Date-41',
						'zAsset- SortToken -CameraRoll-42',
						'zAddAssetAttr-Date Created Source-43',
						'zAsset-Date Created-44',
						'zCldMast-Creation Date-45',
						'zIntResou-CldMst Date Created-46',
						'zAddAssetAttr-Time Zone Name-47',
						'zAddAssetAttr-Time Zone Offset-48',
						'zAddAssetAttr-Inferred Time Zone Offset-49',
						'zAddAssetAttr-EXIF-String-50',
						'zAsset-Modification Date-51',
						'zAsset-Last Shared Date-52',
						'zCldMast-Cloud Local State-53',
						'zCldMast-Import Date-54',
						'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-55',
						'zAddAssetAttr-Import Session ID-56',
						'zAddAssetAttr-Alt Import Image Date-57',
						'zCldMast-Import Session ID- AirDrop-StillTesting-58',
						'zAsset-Cloud Batch Publish Date-59',
						'zAsset-Cloud Server Publish Date-60',
						'zAsset-Cloud Download Requests-61',
						'zAsset-Cloud Batch ID-62',
						'zAddAssetAttr-Upload Attempts-63',
						'zAsset-Latitude-64',
						'zExtAttr-Latitude-65',
						'zAsset-Longitude-66',
						'zExtAttr-Longitude-67',
						'zAddAssetAttr-GPS Horizontal Accuracy-68',
						'zAddAssetAttr-Location Hash-69',
						'zAddAssetAttr-Shifted Location Valid-70',
						'zAddAssetAttr-Shifted Location Data-71',
						'zAddAssetAttr-Reverse Location Is Valid-72',
						'zAddAssetAttr-Reverse Location Data-73',
						'AAAzCldMastMedData-zOPT-74',
						'zAddAssetAttr-Media Metadata Type-75',
						'AAAzCldMastMedData-Data-76',
						'CldMasterzCldMastMedData-zOPT-77',
						'zCldMast-Media Metadata Type-78',
						'CMzCldMastMedData-Data-79',
						'zAsset-Search Index Rebuild State-80',
						'zAddAssetAttr-Syndication History-81',
						'zMedAnlyAstAttr-Syndication Processing Version-82',
						'zMedAnlyAstAttr-Syndication Processing Value-83',
						'zAsset-Orientation-84',
						'zAddAssetAttr-Original Orientation-85',
						'zAsset-Kind-86',
						'zAsset-Kind-Sub-Type-87',
						'zAddAssetAttr-Cloud Kind Sub Type-88',
						'zAsset-Playback Style-89',
						'zAsset-Playback Variation-90',
						'zAsset-Video Duration-91',
						'zExtAttr-Duration-92',
						'zAsset-Video CP Duration-93',
						'zAddAssetAttr-Video CP Duration Time Scale-94',
						'zAsset-Video CP Visibility State-95',
						'zAddAssetAttr-Video CP Display Value-96',
						'zAddAssetAttr-Video CP Display Time Scale-97',
						'zIntResou-Datastore Class ID-98',
						'zAsset-Cloud Placeholder Kind-99',
						'zIntResou-Local Availability-100',
						'zIntResou-Local Availability Target-101',
						'zIntResou-Cloud Local State-102',
						'zIntResou-Remote Availability-103',
						'zIntResou-Remote Availability Target-104',
						'zIntResou-Transient Cloud Master-105',
						'zIntResou-Side Car Index-106',
						'zIntResou- File ID-107',
						'zIntResou-Version-108',
						'zAddAssetAttr- Original-File-Size-109',
						'zIntResou-Resource Type-110',
						'zIntResou-Datastore Sub-Type-111',
						'zIntResou-Cloud Source Type-112',
						'zIntResou-Data Length-113',
						'zIntResou-Recipe ID-114',
						'zIntResou-Cloud Last Prefetch Date-115',
						'zIntResou-Cloud Prefetch Count-116',
						'zIntResou- Cloud-Last-OnDemand Download-Date-117',
						'zIntResou-UniformTypeID_UTI_Conformance_Hint-118',
						'zIntResou-Compact-UTI-119',
						'zAsset-Uniform Type ID-120',
						'zAsset-Original Color Space-121',
						'zCldMast-Uniform_Type_ID-122',
						'zCldMast-Full Size JPEG Source-123',
						'zAsset-HDR Gain-124',
						'zAsset-zHDR_Type-125',
						'zExtAttr-Codec-126',
						'zIntResou-Codec Four Char Code Name-127',
						'zCldMast-Codec Name-128',
						'zCldMast-Video Frame Rate-129',
						'zCldMast-Placeholder State-130',
						'zAsset-Depth_Type-131',
						'zAsset-Avalanche UUID-132',
						'zAsset-Avalanche_Pick_Type-BurstAsset-133',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-134',
						'zAddAssetAttr-Cloud Recovery State-135',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-136',
						'zAsset-Deferred Processing Needed-137',
						'zAsset-Video Deferred Processing Needed-138',
						'zAddAssetAttr-Deferred Photo Identifier-139',
						'zAddAssetAttr-Deferred Processing Candidate Options-140',
						'zAsset-Has Adjustments-Camera-Effects-Filters-141',
						'zAsset-Adjustment Timestamp-142',
						'zAddAssetAttr-Editor Bundle ID-143',
						'zAddAssetAttr-Montage-144',
						'zAsset-Favorite-145',
						'zAsset-Hidden-146',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-147',
						'zAsset-Trashed Date-148',
						'zAsset-Trashed by Participant= zSharePartic_zPK-149',
						'zAsset-Delete-Reason-150',
						'zIntResou-Trash State-151',
						'zIntResou-Trashed Date-152',
						'zAsset-Cloud Delete State-153',
						'zIntResou-Cloud Delete State-154',
						'zAddAssetAttr-PTP Trashed State-155',
						'zIntResou-PTP Trashed State-156',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-157',
						'zMedAnlyAstAttr-Media Analysis Timestamp-158',
						'zAsset-Analysis State Modificaion Date-159',
						'zAddAssetAttr- Pending View Count-160',
						'zAddAssetAttr- View Count-161',
						'zAddAssetAttr- Pending Play Count-162',
						'zAddAssetAttr- Play Count-163',
						'zAddAssetAttr- Pending Share Count-164',
						'zAddAssetAttr- Share Count-165',
						'zAddAssetAttr-Allowed for Analysis-166',
						'zAddAssetAttr-Scene Analysis Version-167',
						'zAddAssetAttr-Scene Analysis is From Preview-168',
						'zAddAssetAttr-Scene Analysis Timestamp-169',
						'zAsset-Duplication Asset Visibility State-170',
						'zAddAssetAttr-Destination Asset Copy State-171',
						'zAddAssetAttr-Duplicate Detector Perceptual Processing State-172',
						'zAddAssetAttr-Source Asset for Duplication Scope ID-173',
						'zCldMast-Source Master For Duplication Scope ID-174',
						'zAddAssetAttr-Source Asset For Duplication ID-175',
						'zCldMast-Source Master for Duplication ID-176',
						'zAddAssetAttr-Variation Suggestions States-177',
						'zAsset-High Frame Rate State-178',
						'zAsset-Video Key Frame Time Scale-179',
						'zAsset-Video Key Frame Value-180',
						'zExtAttr-ISO-181',
						'zExtAttr-Metering Mode-182',
						'zExtAttr-Sample Rate-183',
						'zExtAttr-Track Format-184',
						'zExtAttr-White Balance-185',
						'zExtAttr-Aperture-186',
						'zExtAttr-BitRate-187',
						'zExtAttr-Exposure Bias-188',
						'zExtAttr-Frames Per Second-189',
						'zExtAttr-Shutter Speed-190',
						'zExtAttr-Slush Scene Bias-191',
						'zExtAttr-Slush Version-192',
						'zExtAttr-Slush Preset-193',
						'zExtAttr-Slush Warm Bias-194',
						'zAsset-Height-195',
						'zAddAssetAttr-Original Height-196',
						'zIntResou-Unoriented Height-197',
						'zAsset-Width-198',
						'zAddAssetAttr-Original Width-199',
						'zIntResou-Unoriented Width-200',
						'zAsset-Thumbnail Index-201',
						'zAddAssetAttr-Embedded Thumbnail Height-202',
						'zAddAssetAttr-Embedded Thumbnail Length-203',
						'zAddAssetAttr-Embedded Thumbnail Offset-204',
						'zAddAssetAttr-Embedded Thumbnail Width-205',
						'zAsset-Packed Acceptable Crop Rect-206',
						'zAsset-Packed Badge Attributes-207',
						'zAsset-Packed Preferred Crop Rect-208',
						'zAsset-Curation Score-209',
						'zAsset-Camera Processing Adjustment State-210',
						'zAsset-Depth Type-211',
						'zAsset-Is Magic Carpet-QuicktimeMOVfile-212',
						'zAddAssetAttr-Orig Resource Choice-213',
						'zAsset-Spatial Type-214',
						'zAddAssetAttr-Spatial Over Capture Group ID-215',
						'zAddAssetAttr-Place Annotation Data-216',
						'zAddAssetAttr-Distance Identity-HEX-217',
						'zAddAssetAttr-Edited IPTC Attributes-218',
						'zAddAssetAttr-Title-Comments via Cloud Website-219',
						'zAddAssetAttr-Accessibility Description-220',
						'zAddAssetAttr-Photo Stream Tag ID-221',
						'zAddAssetAttr-Share Type-222',
						'zAddAssetAttr-Library Scope Asset Contributors To Update-223',
						'zAsset-Overall Aesthetic Score-224',
						'zAsset-zENT-225',
						'zAsset-zOPT-226',
						'zAsset-Master= zCldMast-zPK-227',
						'zAsset-Extended Attributes= zExtAttr-zPK-228',
						'zAsset-Import Session Key-229',
						'zAsset-Photo Analysis Attributes Key-230',
						'zAsset-FOK-Cloud Feed Asset Entry Key-231',
						'zAsset-Computed Attributes Asset Key-232',
						'zAsset-Promotion Score-233',
						'zAsset-Iconic Score-234',
						'zAsset-Media Analysis Attributes Key-235',
						'zAsset-Media Group UUID-236',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-237',
						'zAsset.Cloud Collection GUID-238',
						'zAddAssetAttr-zENT-239',
						'ZAddAssetAttr-zOPT-240',
						'zAddAssetAttr-zAsset= zAsset_zPK-241',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-242',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-243',
						'zAddAssetAttr-Public Global UUID-244',
						'zAddAssetAttr-Original Assets UUID-245',
						'zAddAssetAttr-Originating Asset Identifier-246',
						'zAddAssetAttr.Adjusted Fingerprint-247',
						'zCldMast-zPK= zAsset-Master-248',
						'zCldMast-zENT-249',
						'zCldMast-zOPT-250',
						'zCldMast-Moment Share Key= zShare-zPK-251',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-252',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-253',
						'zCldMast-Originating Asset ID-254',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-255',
						'CMzCldMastMedData-zENT-256',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-257',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-258',
						'AAAzCldMastMedData-zENT-259',
						'AAAzCldMastMedData-CldMast key-260',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-261',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-262',
						'zExtAttr-zENT-263',
						'zExtAttr-zOPT-264',
						'zExtAttr-Asset Key-265',
						'zIntResou-zPK-266',
						'zIntResou-zENT-267',
						'zIntResou-zOPT-268',
						'zIntResou-Asset= zAsset_zPK-269',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-270',
						'zMedAnlyAstAttr-zEnt-271',
						'zMedAnlyAstAttr-zOpt-272',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-273')
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
		'description': 'Parses iOS asset records from PhotoData-Photos.sqlite ZINTERNALRESOURCE and'
		' other tables. This and other related parsers should provide data for investigative'
		' analysis of assets being stored locally on the device verses assets being stored in'
		' iCloud Photos as the result of optimization. This is very large query and script,'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results.',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '1.0',
		'date': '2024-04-19',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-Asset_IntResou-Optimization',
		'notes': '',
		'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
		'function': 'get_ph50intresouoptimzdataphdapsql'
	},
	'Ph50-2-Asset_IntResou-SyndPL': {
		'name': 'SyndPL Photos.sqlite 50.2 Asset IntResource Optimization Data',
		'description': 'Parses iOS 17 asset records from Syndication.photos.library-database-Photos.sqlite'
		' ZINTERNALRESOURCE and and other tables. This and other related parsers should'
		' provide data for investigative analysis of assets being stored locally on the'
		' device verses assets being stored in iCloud Photos as the result of optimization.'
		' This is very large query and script, I recommend opening the TSV generated report'
		' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer'
		' to view, search, and filter the results.',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '1.0',
		'date': '2024-04-19',
		'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
		'category': 'Photos.sqlite-Syndication_PL_Artifacts',
		'notes': '',
		'paths': '*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',
		'function': 'get_ph50intresouoptimzdatasyndpl'
	}
}
