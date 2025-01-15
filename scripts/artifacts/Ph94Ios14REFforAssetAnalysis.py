__artifacts_v2__ = {
	'Ph94_1iOS14RefforAssetAnalysisPhDaPsql': {
		'name': 'Ph94.1-iOS14_Ref_for_Asset_Analysis-PhDaPsql',
		'description': 'Parses asset records from PhotoData-Photos.sqlite. This parser includes the largest'
		' set of decoded data based on testing and research conducted by Scott Koenig'
		' https://theforensicscooter.com/. I recommend opening the TSV generated reports'
		' with Zimmermans EZTools https://ericzimmerman.github.io/#!index.md TimelineExplorer'
		' to view, search and filter the results.',
		'author': 'Scott Koenig',
		'version': '5.0',
		'date': '2025-01-05',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-R-Reference_for_Asset_Analysis',
		'notes': '',
		'paths': ('*/PhotoData/Photos.sqlite*',),
		"output_types": ["standard", "tsv"]
	},
	'Ph94_2iOS14RefforAssetAnalysisSyndPL': {
		'name': 'Ph94.2-iOS14_Ref_for_Asset_Analysis-SyndPL',
		'description': 'Parses asset records from Syndication.photoslibrary-database-Photos.sqlite.'
		' This parser includes the largest set of decoded data based on testing and research'
		' conducted by Scott Koenig https://theforensicscooter.com/. I recommend opening the'
		' TSV generated reports with Zimmermans EZTools https://ericzimmerman.github.io/#!index.md'
		' TimelineExplorer to view, search and filter the results.',
		'author': 'Scott Koenig',
		'version': '5.0',
		'date': '2025-01-05',
		'requirements': 'Acquisition that contains Syndication.photoslibrary-database-Photos.sqlite',
		'category': 'Photos.sqlite-R-Reference_for_Asset_Analysis',
		'notes': '',
		'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
		"output_types": ["standard", "tsv", "none"]
	}
}

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph94_1iOS14RefforAssetAnalysisPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
	for source_path in files_found:
		source_path = str(source_path)

		if source_path.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if (version.parse(iosversion) <= version.parse("13.7")) or (version.parse(iosversion) >= version.parse("15")):
		logfunc("Unsupported version for PhotoData-Photos.sqlite for iOS " + iosversion)
		return (), [], source_path
	if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
		source_path = get_file_path(files_found, "Photos.sqlite")
		if source_path is None or not os.path.exists(source_path):
			logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
			return (), [], source_path
		data_list = []

		query = '''
		SELECT
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		CASE zAsset.ZCOMPLETE
			WHEN 1 THEN '1-Yes-1'
		END AS 'zAsset Complete',
		zAsset.Z_PK AS 'zAsset-zPK-4QueryStart',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK-4QueryStart',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb-4QueryStart',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint-4TableStart',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint-4TableStart',
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
			WHEN 3 THEN '3-LPLPs-Asset_or_SWYPs-Asset_NoAuto-Display-3'
			WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
			WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
			WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
			WHEN 7 THEN '7-StillTesting-7'
			WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
			WHEN 12 THEN '12-SWY-Syndicaion-PL-Asset_Auto-Display_In_LPL-12'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
		END AS 'zAsset-Saved Asset Type',
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
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
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID-4QueryStart',
		DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting- 4QueryStart',
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
		ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID-4QueryStart',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4QueryStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4QueryStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4QueryStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4QueryStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4QueryStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4QueryStart',
		CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'ParentzGenAlbum-Cloud-Local-State-4QueryStart',
		CASE zGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'zGenAlbum-Cloud_Local_State-4QueryStart',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Cloud Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Start Date- 4QueryStart',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- End Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date- 4QueryStart',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title- 4QueryStart',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied- 4QueryStart',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY- 4QueryStart',
		zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle ID- 4QueryStart',
		CASE zGenAlbum.Z_ENT
			WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
			WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
			WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
			WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
			WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
		END AS 'zGenAlbum-zENT- Entity- 4QueryStart',
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
		END AS 'ParentzGenAlbum- Kind- 4QueryStart',
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
		END AS 'zGenAlbum-Album Kind- 4QueryStart',		
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
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID-4TableStart',
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
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier-4QueryStart',
		zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		zUnmAdj.ZUUID AS 'zUnmAdj-UUID-4TableStart',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		DateTime(zUnmAdj.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zUnmAdj-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
		zUnmAdj.ZEDITORLOCALIZEDNAME AS 'zUnmAdj-Editor Localized Name',
		zUnmAdj.ZADJUSTMENTFORMATIDENTIFIER AS 'zUnmAdj-Adjustment Format ID',
		zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
		CASE zUnmAdj.ZADJUSTMENTRENDERTYPES
			WHEN 0 THEN '0-Standard or Portrait with erros-0'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Portrait-2'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTRENDERTYPES || ''
		END AS 'zUnmAdj-Adjustment Render Types',
		CASE zUnmAdj.ZADJUSTMENTFORMATVERSION
			WHEN 1.0 THEN '1.0-Markup-1.0'
			WHEN 1.1 THEN '1.1-Slow-Mo-1.1'
			WHEN 1.2 THEN '1.2-StillTesting'
			WHEN 1.3 THEN '1.3-StillTesting'
			WHEN 1.4 THEN '1.4-Filter-1.4'
			WHEN 1.5 THEN '1.5-Adjust-1.5'
			WHEN 1.6 THEN '1.6-Video-Trim-1.6'
			WHEN 1.7 THEN '1.7-StillTesting'
			WHEN 1.8 THEN '1.8-StillTesting'
			WHEN 1.9 THEN '1.9-StillTesting'
			WHEN 2.0 THEN '2.0-ScreenshotServices-2.0'
			ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTFORMATVERSION || ''
		END AS 'zUnmAdj-Adjustment Format Version',
		zUnmAdj.ZADJUSTMENTBASEIMAGEFORMAT AS 'zUnmAdj-Adjustment Base Image Format',
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
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type-4TableStart',
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
		zShare.ZTHUMBNAILIMAGEDATA AS 'zShare-Thumbnail Image Data',
		SPLzShare.ZTHUMBNAILIMAGEDATA AS 'SPLzShare-Thumbnail Image Data',
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
		zAddAssetAttr.ZORIGINALRESOURCECHOICE AS 'zAddAssetAttr-Orig Resource Choice',
		zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
		zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
		zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity',
		zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
		zAssetDes.ZLONGDESCRIPTION AS 'zAssetDes-Long Description',
		zAddAssetAttr.ZASSETDESCRIPTION AS 'zAddAssetAttr-Asset Description',
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
		zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
		zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
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
		zCldSharedComment.ZCOMMENTTYPE AS 'zCldSharedComment-Type',
		zCldSharedComment.ZCOMMENTTEXT AS 'zCldSharedComment-Comment Text',
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
		CASE zAddAssetAttr.ZSHARETYPE
			WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
			WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
		END AS 'zAddAssetAttr-Share Type',
		zShare.ZUUID AS 'zShare-UUID-CMM-4TableStart',
		SPLzShare.ZUUID AS 'SPLzShare-UUID-SPL-4TableStart',
		CASE zShare.Z_ENT
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
		END AS 'zShare-zENT-CMM',
		CASE SPLzShare.Z_ENT
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.Z_ENT || ''
		END AS 'SPLzShare-zENT-SPL',
		CASE zShare.ZSTATUS
			WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
		END AS 'zShare-Status-CMM',
		CASE SPLzShare.ZSTATUS
			WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSTATUS || ''
		END AS 'SPLzShare-Status-SPL',
		CASE zShare.ZSCOPETYPE
			WHEN 2 THEN '2-iCloudLink-CMMoment-2'
			WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
		END AS 'zShare-Scope Type-CMM',
		CASE SPLzShare.ZSCOPETYPE
			WHEN 2 THEN '2-iCloudLink-CMMoment-2'
			WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSCOPETYPE || ''
		END AS 'SPLzShare-Scope Type-SPL',
		CASE zShare.ZLOCALPUBLISHSTATE
			WHEN 2 THEN '2-Published-2'
			ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
		END AS 'zShare-Local Publish State-CMM',
		CASE SPLzShare.ZLOCALPUBLISHSTATE
			WHEN 2 THEN '2-Published-2'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZLOCALPUBLISHSTATE || ''
		END AS 'SPLzShare-Local Publish State-SPL',
		CASE zShare.ZPUBLICPERMISSION
			WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
			WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
			ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
		END AS 'zShare-Public Permission-CMM',
		CASE SPLzShare.ZPUBLICPERMISSION
			WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
			WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZPUBLICPERMISSION || ''
		END AS 'SPLzShare-Public Permission-SPL',
		zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID-CMM',
		SPLzShare.ZORIGINATINGSCOPEIDENTIFIER AS 'SPLzShare-Originating Scope ID-SPL',
		zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID-CMM',
		SPLzShare.ZSCOPEIDENTIFIER AS 'SPLzShare-Scope ID-SPL',
		zShare.ZTITLE AS 'zShare-Title-CMM',
		SPLzShare.ZTITLE AS 'SPLzShare-Title-SPL',
		zShare.ZSHAREURL AS 'zShare-Share URL-CMM',
		SPLzShare.ZSHAREURL AS 'SPLzShare-Share URL-SPL',
		DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date-CMM',
		DateTime(SPLzShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Creation Date-SPL',
		DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date-CMM',
		DateTime(SPLzShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Start Date-SPL',
		DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date-CMM',
		DateTime(SPLzShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-End Date-SPL',
		DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date-CMM',
		DateTime(SPLzShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Expiry Date-SPL',
		zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
		SPLzShare.ZASSETCOUNT AS 'SPLzShare-Asset Count-SPL',
		zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
		SPLzShare.ZPHOTOSCOUNT AS 'SPLzShare-Photos Count-CMM-SPL',
		zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
		SPLzShare.ZUPLOADEDPHOTOSCOUNT AS 'SPLzShare-Uploaded Photos Count-SPL',
		zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
		SPLzShare.ZVIDEOSCOUNT AS 'SPLzShare-Videos Count-SPL',
		zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
		SPLzShare.ZUPLOADEDVIDEOSCOUNT AS 'SPLzShare-Uploaded Videos Count-SPL',
		zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',
		SPLzShare.ZFORCESYNCATTEMPTED AS 'SPLzShare-Force Sync Attempted-SPL',
		CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-CMM-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'zShare-Should Notify On Upload Completion-CMM',
		CASE SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-SPL-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'SPLzShare-Should Notify On Upload Completion-SPL',
		CASE zShare.ZTRASHEDSTATE
			WHEN 0 THEN '0-Not_in_Trash-0'
			WHEN 1 THEN '1-In_Trash-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
		END AS 'zShare-Trashed State-CMM',
		CASE SPLzShare.ZTRASHEDSTATE
			WHEN 0 THEN '0-Not_in_Trash-0'
			WHEN 1 THEN '1-In_Trash-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZTRASHEDSTATE || ''
		END AS 'SPLzShare-Trashed State-SPL',
		CASE zShare.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Not Deleted-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
		END AS 'zShare-Cloud Delete State-CMM',
		CASE SPLzShare.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Not Deleted-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZCLOUDDELETESTATE || ''
		END AS 'SPLzShare-Cloud Delete State-SPL',
		CASE zShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'zShare-Should Ignor Budgets-CMM',
		CASE SPLzShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'SPLzShare-Should Ignor Budgets-SPL',
		zSharePartic.ZUUID AS 'zSharePartic-UUID-4TableStart',
		SPLzSharePartic.ZUUID AS 'SPLzSharePartic-UUID-4TableStart',
		CASE zSharePartic.ZACCEPTANCESTATUS
			WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
			WHEN 2 THEN '2-Invite-Accepted-2'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
		END AS 'zSharePartic-Acceptance Status',
		CASE SPLzSharePartic.ZACCEPTANCESTATUS
			WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
			WHEN 2 THEN '2-Invite-Accepted-2'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZACCEPTANCESTATUS || ''
		END AS 'SPLzSharePartic-Acceptance Status',
		CASE zSharePartic.ZISCURRENTUSER
			WHEN 0 THEN '0-Participant-Not_CloudStorageOwner-0'
			WHEN 1 THEN '1-Participant-Is_CloudStorageOwner-1'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
		END AS 'zSharePartic-Is Current User',
		CASE SPLzSharePartic.ZISCURRENTUSER
			WHEN 0 THEN '0-Participant-Not_CloudStorageOwner-0'
			WHEN 1 THEN '1-Participant-Is_CloudStorageOwner-1'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
		END AS 'SPLzSharePartic-Is Current User',
		CASE zSharePartic.ZROLE
			WHEN 1 THEN '1-Participant-is-Owner-Role-1'
			WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
		END AS 'zSharePartic-Role',
		CASE SPLzSharePartic.ZROLE
			WHEN 1 THEN '1-Participant-is-Owner-Role-1'
			WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
		END AS 'SPLzSharePartic-Role',
		CASE zSharePartic.ZPERMISSION
			WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
		END AS 'zSharePartic-Premission',
		CASE SPLzSharePartic.ZPERMISSION
			WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZPERMISSION || ''
		END AS 'SPLzSharePartic-Premission',
		zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
		SPLzSharePartic.ZUSERIDENTIFIER AS 'SPLzSharePartic-User ID',
		SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK-4TableStart',
		zSharePartic.Z_PK AS 'zSharePartic-zPK-4TableStart',
		zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
		SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
		zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
		SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
		ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID-4TableStart',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4TableStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4TableStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4TableStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4TableStart',
		CASE zAlbumList.ZNEEDSREORDERINGNUMBER
			WHEN 1 THEN '1-Yes-1'
			ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
		END AS 'zAlbumList-Needs Reordering Number',
		CASE zGenAlbum.Z_ENT
			WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
			WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
			WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
			WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
			WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
		END AS 'zGenAlbum-zENT- Entity',
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
		CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'ParentzGenAlbum-Cloud-Local-State',
		CASE zGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'zGenAlbum-Cloud_Local_State',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY',
		zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle ID',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
		ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
		zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',
		CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
			WHEN 1 THEN 'No-1'
			WHEN 24 THEN '24-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
		END AS 'ParentzGenAlbum-Pending Items Type',
		CASE zGenAlbum.ZPENDINGITEMSTYPE
			WHEN 1 THEN 'No-1'
			WHEN 24 THEN '24-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
		END AS 'zGenAlbum-Pending Items Type',
		zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
		zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',
		zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
		ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
		zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',
		CASE zGenAlbum.ZHASUNSEENCONTENT
			WHEN 0 THEN 'No Unseen Content-StillTesting-0'
			WHEN 1 THEN 'Unseen Content-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
		END AS 'zGenAlbum-Has Unseen Content',
		zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',
		CASE zGenAlbum.ZISOWNED
			WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
			WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
		END AS 'zGenAlbum-is Owned',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
			WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
			WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
		END AS 'zGenAlbum-Cloud Relationship State',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
			WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
		END AS 'zGenAlbum-Cloud Relationship State Local',
		zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',
		zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',
		zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',
		zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
		zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',
		zAsset.ZCLOUDOWNERHASHEDPERSONID AS 'zAsset-Cloud Owner Hashed Person ID',
		zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
		END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
		END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
			WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
		END AS 'zGenAlbum-Cloud Album Sub Type',
		DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Contribution Date',
		DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Last Interesting Change Date',
		CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
		END AS 'zGenAlbum-Cloud Notification Enabled',
		CASE ParentzGenAlbum.ZISPINNED
			WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
			WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
		END AS 'ParentzGenAlbum-Pinned',
		CASE zGenAlbum.ZISPINNED
			WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
			WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
		END AS 'zGenAlbum-Pinned',
		CASE ParentzGenAlbum.ZCUSTOMSORTKEY
			WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
			WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
			WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
		END AS 'ParentzGenAlbum-Custom Sort Key',
		CASE zGenAlbum.ZCUSTOMSORTKEY
			WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
			WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
			WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
		END AS 'zGenAlbum-Custom Sort Key',
		CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
			WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
			WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
		END AS 'ParentzGenAlbum-Custom Sort Ascending',
		CASE zGenAlbum.ZCUSTOMSORTASCENDING
			WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
			WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
		END AS 'zGenAlbum-Custom Sort Ascending',
		CASE ParentzGenAlbum.ZISPROTOTYPE
			WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
			WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
		END AS 'ParentzGenAlbum-Is Prototype',
		CASE zGenAlbum.ZISPROTOTYPE
			WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
			WHEN 1 THEN 'zGenAlbum-Prototype-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
		END AS 'zGenAlbum-Is Prototype',
		CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'ParentzGenAlbum-Project Document Type',
		CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'zGenAlbum-Project Document Type',
		CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'ParentzGenAlbum-Custom Query Type',
		CASE zGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'zGenAlbum-Custom Query Type',
		CASE ParentzGenAlbum.ZTRASHEDSTATE
			WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
			WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
		END AS 'ParentzGenAlbum-Trashed State',
		DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
		CASE zGenAlbum.ZTRASHEDSTATE
			WHEN 0 THEN 'zGenAlbum Not In Trash-0'
			WHEN 1 THEN 'zGenAlbum Album In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
		END AS 'zGenAlbum-Trashed State',
		DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
		CASE ParentzGenAlbum.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
			WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
		END AS 'ParentzGenAlbum-Cloud Delete State',
		CASE zGenAlbum.ZCLOUDDELETESTATE
			WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
			WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
		END AS 'zGenAlbum-Cloud Delete State',
		CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
			WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
			WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
		END AS 'zGenAlbum-Cloud Owner Whitelisted',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
		END AS 'zGenAlbum-Cloud Local Public URL Enabled',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
			WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
		END AS 'zGenAlbum-Cloud Public URL Enabled',
		zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',
		zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',
		zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',
		zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',
		zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
		zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
		CASE zCldShareAlbumInvRec.ZISMINE
			WHEN 0 THEN 'Not My Invitation-0'
			WHEN 1 THEN 'My Invitation-1'
			ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
		END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
		CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
			WHEN 0 THEN '0-StillTesting-0'
			WHEN 1 THEN '1-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
		END AS 'zCldShareAlbumInvRec-Invitation State Local',
		CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
			WHEN 1 THEN 'Shared Album Invitation Pending-1'
			WHEN 2 THEN 'Shared Album Invitation Accepted-2'
			WHEN 3 THEN 'Shared Album Invitation Declined-3'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
		END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
		DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldShareAlbumInvRec-Subscription Date',
		zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
		zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
		zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
		zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
		zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',
		zGenAlbum.ZKEYASSETFACEIDENTIFIER AS 'zGenAlbum-Key Asset Face ID',
		CASE
			WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
			ELSE 'Face Area Points Not Detected in zAsset'
		END AS 'zFaceCrop-Face Area Points',
		zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
		CASE zDetFace.ZASSETVISIBLE
			WHEN 0 THEN 'Asset Not Visible Photo Library-0'
			WHEN 1 THEN 'Asset Visible Photo Library-1'
			ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
		END AS 'zDetFace-Asset Visible',
		zPerson.ZFACECOUNT AS 'zPerson-Face Count',
		zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
		zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
		zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
		zDetFace.ZUUID AS 'zDetFace-UUID-4TableStart',
		zPerson.ZPERSONUUID AS 'zPerson-Person UUID-4TableStart',
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
			WHEN 2 THEN '2-Verified-Has-Person-URI'
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
		zFaceCrop.ZUUID AS 'zFaceCrop-UUID-4TableStart',
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
			WHEN 1 THEN 'Infant-Toddler Age Type-1'
			WHEN 2 THEN 'Toddler-Child Age Type-2'
			WHEN 3 THEN 'Child-Young Adult Age Type-3'
			WHEN 4 THEN 'Young Adult-Adult Age Type-4'
			WHEN 5 THEN 'Adult-5'
			ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
		END AS 'zPerson-Age Type Estimate',
		CASE zDetFace.ZAGETYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Infant-Toddler Age Type-1'
			WHEN 2 THEN 'Toddler-Child Age Type-2'
			WHEN 3 THEN 'Child-Young Adult Age Type-3'
			WHEN 4 THEN 'Young Adult-Adult Age Type-4'
			WHEN 5 THEN 'Adult-5'
			ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
		END AS 'zDetFace-Age Type Estimate',
		CASE zDetFace.ZHAIRCOLORTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Black-Brown Hair Color-1'
			WHEN 2 THEN 'Brown-Blonde Hair Color-2'
			WHEN 3 THEN 'Brown-Red Hair Color-3'
			WHEN 4 THEN 'Red-White Hair Color-4'
			WHEN 5 THEN 'StillTesting-Artifical-5'
			WHEN 6 THEN 'White-Bald Hair Color-6'
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
		END AS 'zDetFace-Hidden-Asset Hidden',
		CASE zDetFace.ZISINTRASH
			WHEN 0 THEN 'Not In Trash-0'
			WHEN 1 THEN 'In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
		END AS 'zDetFace-In Trash-Recently Deleted',
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
		zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID-4TableStart',
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
		zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID-4TableStart',
		zMemory.Z_PK AS 'zMemory-zPK',
		z3MemoryBCAs.Z_3CURATEDASSETS AS 'z3MemoryBCAs-3CuratedAssets = zAsset-zPK',
		z3MemoryBCAs.Z_40MEMORIESBEINGCURATEDASSETS AS 'z3MemoryBCAs-40MemoriesBeingCuratedAssets = zMemory-zPK',
		z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-3ExtCuratedAssets = zAsset-zPK',
		z3MemoryBECAs.Z_40MEMORIESBEINGEXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-40MemoriesBeingExtCuratedAssets = zMemory-zPK',
		z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AS 'z3MemoryBMCAs-3MovieCuratedAssets = zAsset-zPK',
		z3MemoryBMCAs.Z_40MEMORIESBEINGMOVIECURATEDASSETS AS 'z3MemoryBMCAs-40MemoriesBeingMovieCuratedAssets = zMemory-zPK',
		z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AS 'z3MemoryBRAs-3RepresentativeAssets = zAsset-zPK',
		z3MemoryBRAs.Z_40MEMORIESBEINGREPRESENTATIVEASSETS AS 'z3MemoryBRAs-40RepresentativeAssets = zMemory-zPK',
		zMemory.ZKEYASSET AS 'zMemory-Key Asset = zAsset-zPK',
		zMemory.ZUUID AS 'zMemory-UUID',
		zMemory.ZSUBTITLE AS 'zMemory-SubTitle',
		zMemory.ZTITLE AS 'zMemory-Title',
		CASE zMemory.ZCATEGORY
			WHEN 1 THEN '1-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 8 THEN '8-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 17 THEN '17-StillTesting'
			WHEN 19 THEN '19-StillTesting'
			WHEN 21 THEN '21-StillTesting'
			WHEN 201 THEN '201-StillTesting'
			WHEN 203 THEN '203-StillTesting'
			WHEN 204 THEN '204-StillTesting'
			WHEN 211 THEN '211-StillTesting'
			WHEN 217 THEN '217-StillTesting'
			WHEN 220 THEN '220-StillTesting'
			WHEN 301 THEN '301-StillTesting'
			WHEN 302 THEN '302-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZCATEGORY || ''
		END AS 'zMemory-Category',
		CASE zMemory.ZSUBCATEGORY
			WHEN 0 THEN '0-StillTesting'
			WHEN 201 THEN '201-StillTesting'
			WHEN 204 THEN '204-StillTesting'
			WHEN 206 THEN '206-StillTesting'
			WHEN 207 THEN '207-StillTesting'
			WHEN 212 THEN '212-StillTesting'
			WHEN 213 THEN '213-StillTesting'
			WHEN 214 THEN '214-StillTesting'
			WHEN 402 THEN '402-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSUBCATEGORY || ''
		END AS 'zMemory-SubCategory',
		DateTime(zMemory.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Creation Date',
		CASE zMemory.ZUSERCREATED
			WHEN 0 THEN 'Memory Not User Created-0'
			WHEN 1 THEN 'Memory User Created-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZUSERCREATED || ''
		END AS 'zMemory-User Created',
		CASE zMemory.ZFAVORITE
			WHEN 0 THEN 'Memory Not Favorite-0'
			WHEN 1 THEN 'Memory Favorite-1'
		END AS 'zMemory-Favorite Memory',
		zMemory.ZSCORE AS 'zMemory-Score',
		zMemory.ZVIEWCOUNT AS 'zMemory-View Count',
		zMemory.ZPLAYCOUNT AS 'zMemory-Play Count',
		zMemory.ZREJECTED AS 'zMemory-Rejected',
		zMemory.ZSHARECOUNT AS 'zMemory-Share Count',
		DateTime(zMemory.ZLASTMOVIEPLAYEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Movie Play Date',
		DateTime(zMemory.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Viewed Date',
		CASE zMemory.ZPENDING
			WHEN 0 THEN 'No-0'
			WHEN 1 THEN 'Yes-1'
			WHEN 2 THEN '2-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZPENDING || ''
		END AS 'zMemory-Pending',
		zMemory.ZPENDINGPLAYCOUNT AS 'zMemory-Pending Play Count Memory',
		zMemory.ZPENDINGSHARECOUNT AS 'zMemory-Pending Share Count Memory',
		zMemory.ZPENDINGVIEWCOUNT AS 'zMemory-Pending View Count Memory',
		CASE zMemory.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZFEATUREDSTATE || ''
		END AS 'zMemory-Featured State',
		zMemory.ZPHOTOSGRAPHVERSION AS 'zMemory-Photos Graph Version',
		zMemory.ZASSETLISTPREDICATE AS 'zMemory-AssetListPredicte',
		CASE zMemory.ZNOTIFICATIONSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZNOTIFICATIONSTATE || ''
		END AS 'zMemory-Notification State',
		CASE zMemory.ZCLOUDLOCALSTATE
			WHEN 0 THEN 'Memory Not Synced with Cloud-0'
			WHEN 1 THEN 'Memory Synced with Cloud-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZCLOUDLOCALSTATE || ''
		END AS 'zMemory-Cloud Local State',
		CASE zMemory.ZCLOUDDELETESTATE
			WHEN 0 THEN 'Memory Not Deleted-0'
			WHEN 1 THEN 'Memory Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZCLOUDDELETESTATE || ''
		END AS 'zMemory-Cloud Delete State',
		YearzMomentList.ZUUID AS 'YearzMomentList-UUID',
		YearzMomentList.Z_PK AS 'YearzMomentList-zPK',
		zMoment.ZYEARMOMENTLIST AS 'zMoment-Year Moment List',
		YearzMomentList.ZSORTINDEX AS 'YearzMomentList-Sort Index',
		CASE YearzMomentList.ZGRANULARITYLEVEL
			WHEN 10 THEN 'Year and Month Moment-10'
			WHEN 20 THEN 'Year Moment-20'
			ELSE 'Unknown-New-Value!: ' || YearzMomentList.ZGRANULARITYLEVEL || ''
		END AS 'YearzMomentList-Granularity Level',
		DateTime(YearzMomentList.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YearzMomentList-Start Date',
		DateTime(YearzMomentList.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'YearzMomentList-Representative Date',
		DateTime(YearzMomentList.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YearzMomentList-End Date',
		CASE YearzMomentList.ZTRASHEDSTATE
			WHEN 0 THEN 'YearzMomentList Not In Trash-0'
			WHEN 1 THEN 'YearzMomentList In Trash-1'
			ELSE 'Unknown-New-Value!: ' || YearzMomentList.ZTRASHEDSTATE || ''
		END AS 'YearzMomentList-Trashed State',
		MegaYMzMomentList.ZUUID AS 'MegaYMzMomentList-UUID',
		MegaYMzMomentList.Z_PK AS 'MegaYMzMomentList-zPK',
		zMoment.ZMEGAMOMENTLIST AS 'zMoment-Mega Moment List',
		MegaYMzMomentList.ZSORTINDEX AS 'MegaYMzMomentList-Sort Index',
		CASE MegaYMzMomentList.ZGRANULARITYLEVEL
			WHEN 10 THEN 'Year and Month Moment-10'
			WHEN 20 THEN 'Year Moment-20'
			ELSE 'Unknown-New-Value!: ' || MegaYMzMomentList.ZGRANULARITYLEVEL || ''
		END AS 'MegaYMzMomentList-Granularity Level',
		DateTime(MegaYMzMomentList.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'MegaYMzMomentList-Start Date',
		DateTime(MegaYMzMomentList.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'MegaYMzMomentList-Representative Date',
		DateTime(MegaYMzMomentList.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'MegaYMzMomentList-End Date',
		CASE MegaYMzMomentList.ZTRASHEDSTATE
			WHEN 0 THEN 'MegaYMzMomentList Not In Trash-0'
			WHEN 1 THEN 'MegaYMzMomentList In Trash-1'
			ELSE 'Unknown-New-Value!: ' || MegaYMzMomentList.ZTRASHEDSTATE || ''
		END AS 'MegaYMzMomentList-Trashed State',
		zMoment.ZUUID AS 'zMoment-UUID',
		zMoment.Z_PK AS 'zMoment-zPK',
		zMoment.ZAGGREGATIONSCORE AS 'zMoment-Aggregation Score',
		DateTime(zMoment.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Start Date',
		DateTime(zMoment.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Representative Date',
		zMoment.ZTIMEZONEOFFSET AS 'zMoment-Timezone Offset',
		DateTime(zMoment.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Modification Date',
		DateTime(zMoment.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-End Date',
		zMoment.ZSUBTITLE AS 'zMoment-SubTitle',
		zMoment.ZTITLE AS 'zMoment-Title',
		CASE zMoment.ZPROCESSEDLOCATION
			WHEN 2 THEN 'No-2'
			WHEN 3 THEN 'Yes-3'
			WHEN 6 THEN 'Yes-6'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZPROCESSEDLOCATION || ''
		END AS 'zMoment-Processed Location',
		zMoment.ZAPPROXIMATELATITUDE AS 'zMoment-Approx Latitude',
		zMoment.ZAPPROXIMATELONGITUDE AS 'zMoment-Approx Longitude',
		CASE zMoment.ZGPSHORIZONTALACCURACY
			WHEN -1.0 THEN '-1.0'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZGPSHORIZONTALACCURACY || ''
		END AS 'zMoment-GPS Horizontal Accuracy',
		zMoment.ZCACHEDCOUNT AS 'zMoment-Cache Count',
		zMoment.ZCACHEDPHOTOSCOUNT AS 'zMoment-Cached Photos Count',
		zMoment.ZCACHEDVIDEOSCOUNT AS 'zMoment-Cached Videos Count',
		CASE zMoment.ZTRASHEDSTATE
			WHEN 0 THEN 'zMoment Not In Trash-0'
			WHEN 1 THEN 'zMoment In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZTRASHEDSTATE || ''
		END AS 'zMoment-Trashed State',
		zMoment.ZHIGHLIGHT AS 'zMoment-Highlight Key',
		zAsset.ZHIGHLIGHTVISIBILITYSCORE AS 'zAsset-Highlight Visibility Score',
		YearParzPhotosHigh.ZUUID AS 'YearParzPhotosHigh-UUID',
		YearParzPhotosHigh.Z_PK AS 'YearParzPhotosHigh-zPK',
		YearParzPhotosHigh.Z_ENT AS 'YearParzPhotosHigh-zENT',
		YearParzPhotosHigh.Z_OPT AS 'YearParzPhotosHigh-zOPT',
		YearParzPhotosHigh.ZPROMOTIONSCORE AS 'YearParzPhotosHigh-Promotion Score',
		YearParzPhotosHigh.ZTITLE AS 'YearParzPhotosHigh-Title',
		YearParzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'YearParzPhotosHigh-Verbose Smart Description',
		DateTime(YearParzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YearParzPhotosHigh-Start Date',
		DateTime(YearParzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YearParzPhotosHigh-End Date',
		YearParzPhotosHigh.ZYEARKEYASSET AS 'YearParzPhotosHigh-Year Key Asset',
		CASE YearParzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZISCURATED || ''
		END AS 'YearParzPhotosHigh-Is Curated',
		CASE YearParzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZKIND || ''
		END AS 'YearParzPhotosHigh-Kind',
		CASE YearParzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZCATEGORY || ''
		END AS 'YearParzPhotosHigh-Category',
		CASE YearParzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-Visible via For You'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'YearParzPhotosHigh-Visibility State',
		CASE YearParzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'YearParzPhotosHigh-Enrichment State',
		YearParzPhotosHigh.ZENRICHMENTVERSION AS 'YearParzPhotosHigh-Enrichment Version',
		YearParzPhotosHigh.ZHIGHLIGHTVERSION AS 'YearParzPhotosHigh-Highlight Version',
		YMParzPhotosHigh.ZUUID AS 'YMParzPhotosHigh-UUID',
		YMParzPhotosHigh.Z_PK AS 'YMParzPhotosHigh-zPK',
		YMParzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'YMParzPhotosHigh-Parent PH Key',
		YMParzPhotosHigh.Z_ENT AS 'YMParzPhotosHigh-zENT',
		YMParzPhotosHigh.Z_OPT AS 'YMParzPhotosHigh-zOPT',
		YMParzPhotosHigh.ZPROMOTIONSCORE AS 'YMParzPhotosHigh-Promotion Score',
		YMParzPhotosHigh.ZTITLE AS 'YMParzPhotosHigh-Title',
		YMParzPhotosHigh.ZSUBTITLE AS 'YMParzPhotosHigh-Subtitle',
		YMParzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'YMParzPhotosHigh-Verbose Smart Description',
		DateTime(YMParzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YMParzPhotosHigh-Start Date',
		DateTime(YMParzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YMParzPhotosHigh-End Date',
		YMParzPhotosHigh.ZMONTHFIRSTASSET AS 'YMParzPhotosHigh-Month First Asset',
		YMParzPhotosHigh.ZMONTHKEYASSET AS 'YMParzPhotosHigh-Month Key Asset',
		CASE YMParzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZISCURATED || ''
		END AS 'YMParzPhotosHigh-Is Curated',
		CASE YMParzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZKIND || ''
		END AS 'YMParzPhotosHigh-Kind',
		CASE YMParzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZCATEGORY || ''
		END AS 'YMParzPhotosHigh-Category',
		CASE YMParzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'YMParzPhotosHigh-Visibility State',
		CASE YMParzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'YMParzPhotosHigh-Enrichment State',
		YMParzPhotosHigh.ZENRICHMENTVERSION AS 'YMParzPhotosHigh-Enrichment Version',
		YMParzPhotosHigh.ZHIGHLIGHTVERSION AS 'YMParzPhotosHigh-Highlight Version',
		DGParzPhotosHigh.ZUUID AS 'DGParzPhotosHigh-UUID',
		DGParzPhotosHigh.Z_PK AS 'DGParzPhotosHigh-zPK',
		DGParzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGParzPhotosHigh-Parent PH Key',
		DGParzPhotosHigh.Z_ENT AS 'DGParzPhotosHigh-zENT',
		DGParzPhotosHigh.Z_OPT AS 'DGParzPhotosHigh-zOPT',
		DGParzPhotosHigh.ZPROMOTIONSCORE AS 'DGParzPhotosHigh-Promotion Score',
		DGParzPhotosHigh.ZTITLE AS 'DGParzPhotosHigh-Title',
		DGParzPhotosHigh.ZSUBTITLE AS 'DGParzPhotosHigh-Subtitle',
		DGParzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGParzPhotosHigh-Verbose Smart Description',
		DateTime(DGParzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGParzPhotosHigh-Start Date',
		DateTime(DGParzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGParzPhotosHigh-End Date',
		DGParzPhotosHigh.ZMONTHFIRSTASSET AS 'DGParzPhotosHigh-Month First Asset',
		DGParzPhotosHigh.ZMONTHKEYASSET AS 'DGParzPhotosHigh-Month Key Asset',
		CASE DGParzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZISCURATED || ''
		END AS 'DGParzPhotosHigh-Is Curated',
		CASE DGParzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZKIND || ''
		END AS 'DGParzPhotosHigh-Kind',
		CASE DGParzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZCATEGORY || ''
		END AS 'DGParzPhotosHigh-Category',
		CASE DGParzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGParzPhotosHigh-Visibility State',
		CASE DGParzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGParzPhotosHigh-Enrichment State',
		DGParzPhotosHigh.ZENRICHMENTVERSION AS 'DGParzPhotosHigh-Enrichment Version',
		DGParzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGParzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGASSETS AS 'zAsset-Highlight Being Assets Key',
		HBAzPhotosHigh.ZUUID AS 'HBAzPhotosHigh-UUID',
		HBAzPhotosHigh.Z_PK AS 'HBAzPhotosHigh-zPK',
		HBAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBAzPhotosHigh-Parent PH Key',
		HBAzPhotosHigh.Z_ENT AS 'HBAzPhotosHigh-zENT',
		HBAzPhotosHigh.Z_OPT AS 'HBAzPhotosHigh-zOPT',
		HBAzPhotosHigh.ZPROMOTIONSCORE AS 'HBAzPhotosHigh-Promotion Score',
		HBAzPhotosHigh.ZTITLE AS 'HBAzPhotosHigh-Title',
		HBAzPhotosHigh.ZSUBTITLE AS 'HBAzPhotosHigh-Subtitle',
		HBAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBAzPhotosHigh-Verbose Smart Description',
		DateTime(HBAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBAzPhotosHigh-Start Date',
		HBAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBAzPhotosHigh Start-Timezone Offset',
		HBAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBAzPhotosHigh-End Timezone Offset',
		DateTime(HBAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBAzPhotosHigh-End Date',
		HBAzPhotosHigh.ZASSETSCOUNT AS 'HBAzPhotosHigh-Asset Count',
		HBAzPhotosHigh.ZSUMMARYCOUNT AS 'HBAzPhotosHigh-Summary Count',
		HBAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBAzPhotosHigh-Extended Count',
		HBAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBAzPhotosHigh-Day Group Assets Count',
		HBAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBAzPhotosHigh-Day Group Ext Assets Count',
		HBAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBAzPhotosHigh-Day Group Summary Assets Count',
		HBAzPhotosHigh.ZKEYASSET AS 'HBAzPhotosHigh-Key Asset',
		CASE HBAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZISCURATED || ''
		END AS 'HBAzPhotosHigh-Is Curated',
		CASE HBAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZTYPE || ''
		END AS 'HBAzPhotosHigh-Type',
		CASE HBAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZKIND || ''
		END AS 'HBAzPhotosHigh-Kind',
		CASE HBAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBAzPhotosHigh-Category',
		CASE HBAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBAzPhotosHigh-Visibility State',
		CASE HBAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZMOOD || ''
		END AS 'HBAzPhotosHigh-Mood',
		CASE HBAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBAzPhotosHigh-Enrichment State',
		HBAzPhotosHigh.ZENRICHMENTVERSION AS 'HBAzPhotosHigh-Enrichment Version',
		HBAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBAzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Highlight Being Extended Assets Key',
		HBEAzPhotosHigh.ZUUID AS 'HBEAzPhotosHigh-UUID',
		HBEAzPhotosHigh.Z_PK AS 'HBEAzPhotosHigh-zPK',
		HBEAzPhotosHigh.Z_ENT AS 'HBEAzPhotosHigh-zENT',
		HBEAzPhotosHigh.Z_OPT AS 'HBEAzPhotosHigh-zOPT',
		HBEAzPhotosHigh.ZPROMOTIONSCORE AS 'HBEAzPhotosHigh-Promotion Score',
		HBEAzPhotosHigh.ZTITLE AS 'HBEAzPhotosHigh-Title',
		HBEAzPhotosHigh.ZSUBTITLE AS 'HBEAzPhotosHigh-Subtitle',
		HBEAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBEAzPhotosHigh-Verbose Smart Description',
		DateTime(HBEAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBEAzPhotosHigh-Start Date',
		HBEAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBEAzPhotosHigh-Start Timezone Offset',
		HBEAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBEAzPhotosHigh-End Timezone Offset',
		DateTime(HBEAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBEAzPhotosHigh-End Date',
		HBEAzPhotosHigh.ZASSETSCOUNT AS 'HBEAzPhotosHigh-Asset Count',
		HBEAzPhotosHigh.ZSUMMARYCOUNT AS 'HBEAzPhotosHigh-Summary Count',
		HBEAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBEAzPhotosHigh-Extended Count',
		HBEAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBEAzPhotosHigh-Day Group Assets Count',
		HBEAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBEAzPhotosHigh-Day Group Ext Assets Count',
		HBEAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBEAzPhotosHigh-Day Group Summary Assets Count',
		HBEAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBEAzPhotosHigh-Parent PH Key',
		HBEAzPhotosHigh.ZYEARKEYASSET AS 'HBEAzPhotosHigh-Year Key Asset',
		HBEAzPhotosHigh.ZMONTHFIRSTASSET AS 'HBEAzPhotosHigh-Month First Asset',
		HBEAzPhotosHigh.ZMONTHKEYASSET AS 'HBEAzPhotosHigh-Month Key Asset',
		HBEAzPhotosHigh.ZKEYASSET AS 'HBEAzPhotosHigh-Key Asset',
		HBEAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'HBEAzPhotosHigh-Parent Day Group PH Key',
		HBEAzPhotosHigh.ZDAYGROUPKEYASSET AS 'HBEAzPhotosHigh-Day Group Key Asset',
		CASE HBEAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZISCURATED || ''
		END AS 'HBEAzPhotosHigh-is Curated',
		CASE HBEAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZTYPE || ''
		END AS 'HBEAzPhotosHigh-Type',
		CASE HBEAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZKIND || ''
		END AS 'HBEAzPhotosHigh-Kind',
		CASE HBEAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBEAzPhotosHigh-Category',
		CASE HBEAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBEAzPhotosHigh-Visibility State',
		CASE HBEAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZMOOD || ''
		END AS 'HBEAzPhotosHigh-Mood',
		CASE HBEAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBEAzPhotosHigh-Enrichment State',
		HBEAzPhotosHigh.ZENRICHMENTVERSION AS 'HBEAzPhotosHigh-Enrichment Version',
		HBEAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBEAzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Highlight Being Summary Assets Key',
		HBSAzPhotosHigh.ZUUID AS 'HBSAzPhotosHigh-UUID',
		HBSAzPhotosHigh.Z_PK AS 'HBSAzPhotosHigh-zPK',
		HBSAzPhotosHigh.Z_ENT AS 'HBSAzPhotosHigh-zENT',
		HBSAzPhotosHigh.Z_OPT AS 'HBSAzPhotosHigh-zOPT',
		HBSAzPhotosHigh.ZPROMOTIONSCORE AS 'HBSAzPhotosHigh-Promotion Score',
		HBSAzPhotosHigh.ZTITLE AS 'HBSAzPhotosHigh-Title',
		HBSAzPhotosHigh.ZSUBTITLE AS 'HBSAzPhotosHigh-Subtitle',
		HBSAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBSAzPhotosHigh-Verbose Smart Description',
		DateTime(HBSAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBSAzPhotosHigh-Start Date',
		HBSAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBSAzPhotosHigh-Start Timezone Offset',
		HBSAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBSAzPhotosHigh-End Timezone Offset',
		DateTime(HBSAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBSAzPhotosHigh-End Date',
		HBSAzPhotosHigh.ZASSETSCOUNT AS 'HBSAzPhotosHigh-Asset Count',
		HBSAzPhotosHigh.ZSUMMARYCOUNT AS 'HBSAzPhotosHigh-Summary Count',
		HBSAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBSAzPhotosHigh-Extended Count',
		HBSAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBSAzPhotosHigh-Day Group Assets Count',
		HBSAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBSAzPhotosHigh-Day Group Ext Assets Count',
		HBSAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBSAzPhotosHigh-Day Group Summary Assets Count',
		HBSAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBSAzPhotosHigh-Parent PH Key',
		HBSAzPhotosHigh.ZYEARKEYASSET AS 'HBSAzPhotosHigh-Year Key Asset',
		HBSAzPhotosHigh.ZMONTHFIRSTASSET AS 'HBSAzPhotosHigh-Month First Asset',
		HBSAzPhotosHigh.ZMONTHKEYASSET AS 'HBSAzPhotosHigh-Month Key Asset',
		HBSAzPhotosHigh.ZKEYASSET AS 'HBSAzPhotosHigh-Key Asset',
		HBSAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'HBSAzPhotosHigh-Parent Day Group PH Key',
		HBSAzPhotosHigh.ZDAYGROUPKEYASSET AS 'HBSAzPhotosHigh-Day Group Key Asset',
		CASE HBSAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZISCURATED || ''
		END AS 'HBSAzPhotosHigh-is Curated',
		CASE HBSAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZTYPE || ''
		END AS 'HBSAzPhotosHigh-Type',
		CASE HBSAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZKIND || ''
		END AS 'HBSAzPhotosHigh-Kind',
		CASE HBSAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBSAzPhotosHigh-Category',
		CASE HBSAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBSAzPhotosHigh-Visibility State',
		CASE HBSAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZMOOD || ''
		END AS 'HBSAzPhotosHigh-Mood',
		CASE HBSAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBSAzPhotosHigh-Enrichment State',
		HBSAzPhotosHigh.ZENRICHMENTVERSION AS 'HBSAzPhotosHigh-Enrichment Version',
		HBSAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBSAzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGKEYASSET AS 'zAsset-Highlight Being Key Asset Key',
		HBKAzPhotosHigh.ZUUID AS 'HBKAzPhotosHigh-UUID',
		HBKAzPhotosHigh.Z_PK AS 'HBKAzPhotosHigh-zPK',
		HBKAzPhotosHigh.Z_ENT AS 'HBKAzPhotosHigh-zENT',
		HBKAzPhotosHigh.Z_OPT AS 'HBKAzPhotosHigh-zOPT',
		HBKAzPhotosHigh.ZPROMOTIONSCORE AS 'HBKAzPhotosHigh-Promotion Score',
		HBKAzPhotosHigh.ZTITLE AS 'HBKAzPhotosHigh-Title',
		HBKAzPhotosHigh.ZSUBTITLE AS 'HBKAzPhotosHigh-Subtitle',
		HBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBKAzPhotosHigh-Verbose Smart Description',
		DateTime(HBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBKAzPhotosHigh-Start Date',
		HBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBKAzPhotosHigh-Start Timezone Offset',
		HBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBKAzPhotosHigh-End Timezone Offset',
		DateTime(HBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBKAzPhotosHigh-End Date',
		HBKAzPhotosHigh.ZASSETSCOUNT AS 'HBKAzPhotosHigh-Asset Count',
		HBKAzPhotosHigh.ZSUMMARYCOUNT AS 'HBKAzPhotosHigh-Summary Count',
		HBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBKAzPhotosHigh-Extended Count',
		HBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBKAzPhotosHigh-Day Group Assets Count',
		HBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBKAzPhotosHigh-Day Group Ext Assets Count',
		HBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBKAzPhotosHigh-Day Group Summary Assets Count',
		HBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBKAzPhotosHigh-Parent PH Key',
		HBKAzPhotosHigh.ZYEARKEYASSET AS 'HBKAzPhotosHigh-Year Key Asset',
		HBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'HBKAzPhotosHigh-Month First Asset',
		HBKAzPhotosHigh.ZMONTHKEYASSET AS 'HBKAzPhotosHigh-Month Key Asset',
		HBKAzPhotosHigh.ZKEYASSET AS 'HBKAzPhotosHigh-Key Asset',
		HBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'HBKAzPhotosHigh-Parent Day Group PH Key',
		HBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'HBKAzPhotosHigh-Day Group Key Asset',
		CASE HBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZISCURATED || ''
		END AS 'HBKAzPhotosHigh-is Curated',
		CASE HBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZTYPE || ''
		END AS 'HBKAzPhotosHigh-Type',
		CASE HBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZKIND || ''
		END AS 'HBKAzPhotosHigh-Kind',
		CASE HBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBKAzPhotosHigh-Category',
		CASE HBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBKAzPhotosHigh-Visibility State',
		CASE HBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZMOOD || ''
		END AS 'HBKAzPhotosHigh-Mood',
		CASE HBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBKAzPhotosHigh-Enrichment State',
		HBKAzPhotosHigh.ZENRICHMENTVERSION AS 'HBKAzPhotosHigh-Enrichment Version',
		HBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBKAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS AS 'zAsset-Day Group Highlight Being Assets Key',
		DGHBAzPhotosHigh.ZUUID AS 'DGHBAzPhotosHigh-UUID',
		DGHBAzPhotosHigh.Z_PK AS 'DGHBAzPhotosHigh-zPK',
		DGHBAzPhotosHigh.Z_ENT AS 'DGHBAzPhotosHigh-zENT',
		DGHBAzPhotosHigh.Z_OPT AS 'DGHBAzPhotosHigh-zOPT',
		DGHBAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBAzPhotosHigh-Promotion Score',
		DGHBAzPhotosHigh.ZTITLE AS 'DGHBAzPhotosHigh-Title',
		DGHBAzPhotosHigh.ZSUBTITLE AS 'DGHBAzPhotosHigh-Subtitle',
		DGHBAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBAzPhotosHigh-Start Date',
		DGHBAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBAzPhotosHigh-Start Timezone Offset',
		DGHBAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBAzPhotosHigh-End Date',
		DGHBAzPhotosHigh.ZASSETSCOUNT AS 'DGHBAzPhotosHigh-Asset Count',
		DGHBAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBAzPhotosHigh-Summary Count',
		DGHBAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBAzPhotosHigh-Extended Count',
		DGHBAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBAzPhotosHigh-Day Group Assets Count',
		DGHBAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBAzPhotosHigh-Day Group Ext Assets Count',
		DGHBAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBAzPhotosHigh-Day Group Summary Assets Count',
		DGHBAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBAzPhotosHigh-Parent PH Key',
		DGHBAzPhotosHigh.ZYEARKEYASSET AS 'DGHBAzPhotosHigh-Year Key Asset',
		DGHBAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBAzPhotosHigh-Month First Asset',
		DGHBAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBAzPhotosHigh-Month Key Asset',
		DGHBAzPhotosHigh.ZKEYASSET AS 'DGHBAzPhotosHigh-Key Asset',
		DGHBAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBAzPhotosHigh-Parent Day Group PH Key',
		DGHBAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBAzPhotosHigh-Day Group Key Asset',
		CASE DGHBAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBAzPhotosHigh-is Curated',
		CASE DGHBAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBAzPhotosHigh-Type',
		CASE DGHBAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZKIND || ''
		END AS 'DGHBAzPhotosHigh-Kind',
		CASE DGHBAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBAzPhotosHigh-Category',
		CASE DGHBAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZVISIBILITYSTATE
		END AS 'DGHBAzPhotosHigh-Visibility State',
		CASE DGHBAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBAzPhotosHigh-Mood',
		CASE DGHBAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBAzPhotosHigh-Enrichment State',
		DGHBAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBAzPhotosHigh-Enrichment Version',
		DGHBAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Day Group Highlight Being Extended Assets Key',
		DGHBEAzPhotosHigh.ZUUID AS 'DGHBEAzPhotosHigh-UUID',
		DGHBEAzPhotosHigh.Z_PK AS 'DGHBEAzPhotosHigh-zPK',
		DGHBEAzPhotosHigh.Z_ENT AS 'DGHBEAzPhotosHigh-zENT',
		DGHBEAzPhotosHigh.Z_OPT AS 'DGHBEAzPhotosHigh-zOPT',
		DGHBEAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBEAzPhotosHigh-Promotion Score',
		DGHBEAzPhotosHigh.ZTITLE AS 'DGHBEAzPhotosHigh-Title',
		DGHBEAzPhotosHigh.ZSUBTITLE AS 'DGHBEAzPhotosHigh-Subtitle',
		DGHBEAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBEAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBEAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBEAzPhotosHigh-Start Date',
		DGHBEAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBEAzPhotosHigh-Start Timezone Offset',
		DGHBEAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBEAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBEAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBEAzPhotosHigh-End Date',
		DGHBEAzPhotosHigh.ZASSETSCOUNT AS 'DGHBEAzPhotosHigh-Asset Count',
		DGHBEAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBEAzPhotosHigh-Summary Count',
		DGHBEAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBEAzPhotosHigh-Extended Count',
		DGHBEAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBEAzPhotosHigh-Day Group Assets Count',
		DGHBEAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBEAzPhotosHigh-Day Group Ext Assets Count',
		DGHBEAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBEAzPhotosHigh-Day Group Summary Assets Count',
		DGHBEAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBEAzPhotosHigh-Parent PH Key',
		DGHBEAzPhotosHigh.ZYEARKEYASSET AS 'DGHBEAzPhotosHigh-Year Key Asset',
		DGHBEAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBEAzPhotosHigh-Month First Asset',
		DGHBEAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBEAzPhotosHigh-Month Key Asset',
		DGHBEAzPhotosHigh.ZKEYASSET AS 'DGHBEAzPhotosHigh-Key Asset',
		DGHBEAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBEAzPhotosHigh-Parent Day Group PH Key',
		DGHBEAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBEAzPhotosHigh-Day Group Key Asset',
		CASE DGHBEAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBEAzPhotosHigh-is Curated',
		CASE DGHBEAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBEAzPhotosHigh-Type',
		CASE DGHBEAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZKIND || ''
		END AS 'DGHBEAzPhotosHigh-Kind',
		CASE DGHBEAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBEAzPhotosHigh-Category',
		CASE DGHBEAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGHBEAzPhotosHigh-Visibility State',
		CASE DGHBEAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBEAzPhotosHigh-Mood',
		CASE DGHBEAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBEAzPhotosHigh-Enrichment State',
		DGHBEAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBEAzPhotosHigh-Enrichment Version',
		DGHBEAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBEAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSET AS 'zAsset-Day Group Highlight Being Key Asset',
		DGHBKAzPhotosHigh.ZUUID AS 'DGHBKAzPhotosHigh-UUID',
		DGHBKAzPhotosHigh.Z_PK AS 'DGHBKAzPhotosHigh-zPK',
		DGHBKAzPhotosHigh.Z_ENT AS 'DGHBKAzPhotosHigh-zENT',
		DGHBKAzPhotosHigh.Z_OPT AS 'DGHBKAzPhotosHigh-zOPT',
		DGHBKAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBKAzPhotosHigh-Promotion Score',
		DGHBKAzPhotosHigh.ZTITLE AS 'DGHBKAzPhotosHigh-Title',
		DGHBKAzPhotosHigh.ZSUBTITLE AS 'DGHBKAzPhotosHigh-Subtitle',
		DGHBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBKAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBKAzPhotosHigh-Start Date',
		DGHBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBKAzPhotosHigh-Start Timezone Offset',
		DGHBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBKAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBKAzPhotosHigh-End Date',
		DGHBKAzPhotosHigh.ZASSETSCOUNT AS 'DGHBKAzPhotosHigh-Asset Count',
		DGHBKAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBKAzPhotosHigh-Summary Count',
		DGHBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBKAzPhotosHigh-Extended Count',
		DGHBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBKAzPhotosHigh-Day Group Assets Count',
		DGHBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBKAzPhotosHigh-Day Group Ext Assets Count',
		DGHBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBKAzPhotosHigh-Day Group Summary Assets Count',
		DGHBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBKAzPhotosHigh-Parent PH Key',
		DGHBKAzPhotosHigh.ZYEARKEYASSET AS 'DGHBKAzPhotosHigh-Year Key Asset',
		DGHBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBKAzPhotosHigh-Month First Asset',
		DGHBKAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBKAzPhotosHigh-Month Key Asset',
		DGHBKAzPhotosHigh.ZKEYASSET AS 'DGHBKAzPhotosHigh-Key Asset',
		DGHBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBKAzPhotosHigh-Parent Day Group PH Key',
		DGHBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBKAzPhotosHigh-Day Group Key Asset',
		CASE DGHBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBKAzPhotosHigh-is Curated',
		CASE DGHBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBKAzPhotosHigh-Type',
		CASE DGHBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZKIND || ''
		END AS 'DGHBKAzPhotosHigh-Kind',
		CASE DGHBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBKAzPhotosHigh-Category',
		CASE DGHBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGHBKAzPhotosHigh-Visibility State',
		CASE DGHBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBKAzPhotosHigh-Mood',
		CASE DGHBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBKAzPhotosHigh-Enrichment State',
		DGHBKAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBKAzPhotosHigh-Enrichment Version',
		DGHBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBKAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Day Group Highlight Being Summary Assets Key',
		DGHBSAzPhotosHigh.ZUUID AS 'DGHBSAzPhotosHigh-UUID',
		DGHBSAzPhotosHigh.Z_PK AS 'DGHBSAzPhotosHigh-zPK',
		DGHBSAzPhotosHigh.Z_ENT AS 'DGHBSAzPhotosHigh-zENT',
		DGHBSAzPhotosHigh.Z_OPT AS 'DGHBSAzPhotosHigh-zOPT',
		DGHBSAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBSAzPhotosHigh-Promotion Score',
		DGHBSAzPhotosHigh.ZTITLE AS 'DGHBSAzPhotosHigh-Title',
		DGHBSAzPhotosHigh.ZSUBTITLE AS 'DGHBSAzPhotosHigh-Subtitle',
		DGHBSAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBSAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBSAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBSAzPhotosHigh-Start Date',
		DGHBSAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBSAzPhotosHigh-Start Timezone Offset',
		DGHBSAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBSAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBSAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBSAzPhotosHigh-End Date',
		DGHBSAzPhotosHigh.ZASSETSCOUNT AS 'DGHBSAzPhotosHigh-Asset Count',
		DGHBSAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBSAzPhotosHigh-Summary Count',
		DGHBSAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBSAzPhotosHigh-Extended Count',
		DGHBSAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBSAzPhotosHigh-Day Group Assets Count',
		DGHBSAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBSAzPhotosHigh-Day Group Ext Assets Count',
		DGHBSAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBSAzPhotosHigh-Day Group Summary Assets Count',
		DGHBSAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBSAzPhotosHigh-Parent PH Key',
		DGHBSAzPhotosHigh.ZYEARKEYASSET AS 'DGHBSAzPhotosHigh-Year Key Asset',
		DGHBSAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBSAzPhotosHigh-Month First Asset',
		DGHBSAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBSAzPhotosHigh-Month Key Asset',
		DGHBSAzPhotosHigh.ZKEYASSET AS 'DGHBSAzPhotosHigh-Key Asset',
		DGHBSAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBSAzPhotosHigh-Parent Day Group PH Key',
		DGHBSAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBSAzPhotosHigh-Day Group Key Asset',
		CASE DGHBSAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBSAzPhotosHigh-is Curated',
		CASE DGHBSAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBSAzPhotosHigh-Type',
		CASE DGHBSAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZKIND || ''
		END AS 'DGHBSAzPhotosHigh-Kind',
		CASE DGHBSAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBSAzPhotosHigh-Category',
		CASE DGHBSAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGHBSAzPhotosHigh-Visibility State',
		CASE DGHBSAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBSAzPhotosHigh-Mood',
		CASE DGHBSAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBSAzPhotosHigh-Enrichment State',
		DGHBSAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBSAzPhotosHigh-Enrichment Version',
		DGHBSAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBSAzPhotosHigh-Highlight Version',
		zAsset.ZMONTHHIGHLIGHTBEINGFIRSTASSET AS 'zAsset-Month Highlight Being First Asset Key',
		MHBFAzPhotosHigh.ZUUID AS 'MHBFAzPhotosHigh-UUID',
		MHBFAzPhotosHigh.Z_PK AS 'MHBFAzPhotosHigh-zPK',
		MHBFAzPhotosHigh.Z_ENT AS 'MHBFAzPhotosHigh-zENT',
		MHBFAzPhotosHigh.Z_OPT AS 'MHBFAzPhotosHigh-zOPT',
		MHBFAzPhotosHigh.ZPROMOTIONSCORE AS 'MHBFAzPhotosHigh-Promotion Score',
		MHBFAzPhotosHigh.ZTITLE AS 'MHBFAzPhotosHigh-Title',
		MHBFAzPhotosHigh.ZSUBTITLE AS 'MHBFAzPhotosHigh-Subtitle',
		MHBFAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'MHBFAzPhotosHigh-Verbose Smart Description',
		DateTime(MHBFAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'MHBFAzPhotosHigh-Start Date',
		MHBFAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'MHBFAzPhotosHigh-Start Timezone Offset',
		MHBFAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'MHBFAzPhotosHigh-End Timezone Offset',
		DateTime(MHBFAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'MHBFAzPhotosHigh-End Date',
		MHBFAzPhotosHigh.ZASSETSCOUNT AS 'MHBFAzPhotosHigh-Asset Count',
		MHBFAzPhotosHigh.ZSUMMARYCOUNT AS 'MHBFAzPhotosHigh-Summary Count',
		MHBFAzPhotosHigh.ZEXTENDEDCOUNT AS 'MHBFAzPhotosHigh-Extended Count',
		MHBFAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'MHBFAzPhotosHigh-Day Group Assets Count',
		MHBFAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'MHBFAzPhotosHigh-Day Group Ext Assets Count',
		MHBFAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'MHBFAzPhotosHigh-Day Group Summary Assets Count',
		MHBFAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'MHBFAzPhotosHigh-Parent PH Key',
		MHBFAzPhotosHigh.ZYEARKEYASSET AS 'MHBFAzPhotosHigh-Year Key Asset',
		MHBFAzPhotosHigh.ZMONTHFIRSTASSET AS 'MHBFAzPhotosHigh-Month First Asset',
		MHBFAzPhotosHigh.ZMONTHKEYASSET AS 'MHBFAzPhotosHigh-Month Key Asset',
		MHBFAzPhotosHigh.ZKEYASSET AS 'MHBFAzPhotosHigh-Key Asset',
		MHBFAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'MHBFAzPhotosHigh-Parent Day Group PH Key',
		MHBFAzPhotosHigh.ZDAYGROUPKEYASSET AS 'MHBFAzPhotosHigh-Day Group Key Asset',
		CASE MHBFAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZISCURATED || ''
		END AS 'MHBFAzPhotosHigh-is Curated',
		CASE MHBFAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZTYPE || ''
		END AS 'MHBFAzPhotosHigh-Type',
		CASE MHBFAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZKIND || ''
		END AS 'MHBFAzPhotosHigh-Kind',
		CASE MHBFAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZCATEGORY || ''
		END AS 'MHBFAzPhotosHigh-Category',
		CASE MHBFAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'MHBFAzPhotosHigh-Visibility State',
		CASE MHBFAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZMOOD || ''
		END AS 'MHBFAzPhotosHigh-Mood',
		CASE MHBFAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'MHBFAzPhotosHigh-Enrichment State',
		MHBFAzPhotosHigh.ZENRICHMENTVERSION AS 'MHBFAzPhotosHigh-Enrichment Version',
		MHBFAzPhotosHigh.ZHIGHLIGHTVERSION AS 'MHBFAzPhotosHigh-Highlight Version',
		zAsset.ZMONTHHIGHLIGHTBEINGKEYASSET AS 'zAsset-Month Highlight Being Key Asset',
		MHBKAzPhotosHigh.ZUUID AS 'MHBKAzPhotosHigh-UUID',
		MHBKAzPhotosHigh.Z_PK AS 'MHBKAzPhotosHigh-zPK',
		MHBKAzPhotosHigh.Z_ENT AS 'MHBKAzPhotosHigh-zENT',
		MHBKAzPhotosHigh.Z_OPT AS 'MHBKAzPhotosHigh-zOPT',
		MHBKAzPhotosHigh.ZPROMOTIONSCORE AS 'MHBKAzPhotosHigh-Promotion Score',
		MHBKAzPhotosHigh.ZTITLE AS 'MHBKAzPhotosHigh-Title',
		MHBKAzPhotosHigh.ZSUBTITLE AS 'MHBKAzPhotosHigh-Subtitle',
		MHBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'MHBKAzPhotosHigh-Verbose Smart Description',
		DateTime(MHBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'MHBKAzPhotosHigh-Start Date',
		MHBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'MHBKAzPhotosHigh-Start Timezone Offset',
		MHBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'MHBKAzPhotosHigh-End Timezone Offset',
		DateTime(MHBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'MHBKAzPhotosHigh-End Date',
		MHBKAzPhotosHigh.ZASSETSCOUNT AS 'MHBKAzPhotosHigh-Asset Count',
		MHBKAzPhotosHigh.ZSUMMARYCOUNT AS 'MHBKAzPhotosHigh-Summary Count',
		MHBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'MHBKAzPhotosHigh-Extended Count',
		MHBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'MHBKAzPhotosHigh-Day Group Assets Count',
		MHBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'MHBKAzPhotosHigh-Day Group Ext Assets Count',
		MHBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'MHBKAzPhotosHigh-Day Group Summary Assets Count',
		MHBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'MHBKAzPhotosHigh-Parent PH Key',
		MHBKAzPhotosHigh.ZYEARKEYASSET AS 'MHBKAzPhotosHigh-Year Key Asset',
		MHBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'MHBKAzPhotosHigh-Month First Asset',
		MHBKAzPhotosHigh.ZMONTHKEYASSET AS 'MHBKAzPhotosHigh-Month Key Asset',
		MHBKAzPhotosHigh.ZKEYASSET AS 'MHBKAzPhotosHigh-Key Asset',
		MHBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'MHBKAzPhotosHigh-Parent Day Group PH Key',
		MHBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'MHBKAzPhotosHigh-Day Group Key Asset',
		CASE MHBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZISCURATED || ''
		END AS 'MHBKAzPhotosHigh-is Curated',
		CASE MHBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZTYPE || ''
		END AS 'MHBKAzPhotosHigh-Type',
		CASE MHBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZKIND || ''
		END AS 'MHBKAzPhotosHigh-Kind',
		CASE MHBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'MHBKAzPhotosHigh-Category',
		CASE MHBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'MHBKAzPhotosHigh-Visibility State',
		CASE MHBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZMOOD || ''
		END AS 'MHBKAzPhotosHigh-Mood',
		CASE MHBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'MHBKAzPhotosHigh-Enrichment State',
		MHBKAzPhotosHigh.ZENRICHMENTVERSION AS 'MHBKAzPhotosHigh-Enrichment Version',
		MHBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'MHBKAzPhotosHigh-Highlight Version',
		zAsset.ZYEARHIGHLIGHTBEINGKEYASSET AS 'zAsset-Year Highlight Being Key Asset',
		YHBKAzPhotosHigh.ZUUID AS 'YHBKAzPhotosHigh-UUID',
		YHBKAzPhotosHigh.Z_PK AS 'YHBKAzPhotosHigh-zPK',
		YHBKAzPhotosHigh.Z_ENT AS 'YHBKAzPhotosHigh-zENT',
		YHBKAzPhotosHigh.Z_OPT AS 'YHBKAzPhotosHigh-zOPT',
		YHBKAzPhotosHigh.ZPROMOTIONSCORE AS 'YHBKAzPhotosHigh-Promotion Score',
		YHBKAzPhotosHigh.ZTITLE AS 'YHBKAzPhotosHigh-Title',
		YHBKAzPhotosHigh.ZSUBTITLE AS 'YHBKAzPhotosHigh-Subtitle',
		YHBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'YHBKAzPhotosHigh-Verbose Smart Description',
		DateTime(YHBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YHBKAzPhotosHigh-Start Date',
		YHBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'YHBKAzPhotosHigh-Start Timezone Offset',
		YHBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'YHBKAzPhotosHigh-End Timezone Offset',
		DateTime(YHBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YHBKAzPhotosHigh-End Date',
		YHBKAzPhotosHigh.ZASSETSCOUNT AS 'YHBKAzPhotosHigh-Asset Count',
		YHBKAzPhotosHigh.ZSUMMARYCOUNT AS 'YHBKAzPhotosHigh-Summary Count',
		YHBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'YHBKAzPhotosHigh-Extended Count',
		YHBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'YHBKAzPhotosHigh-Day Group Assets Count',
		YHBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'YHBKAzPhotosHigh-Day Group Ext Assets Count',
		YHBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'YHBKAzPhotosHigh-Day Group Summary Assets Count',
		YHBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'YHBKAzPhotosHigh-Parent PH Key',
		YHBKAzPhotosHigh.ZYEARKEYASSET AS 'YHBKAzPhotosHigh-Year Key Asset',
		YHBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'YHBKAzPhotosHigh-Month First Asset',
		YHBKAzPhotosHigh.ZMONTHKEYASSET AS 'YHBKAzPhotosHigh-Month Key Asset',
		YHBKAzPhotosHigh.ZKEYASSET AS 'YHBKAzPhotosHigh-Key Asset',
		YHBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'YHBKAzPhotosHigh-Parent Day Group PH Key',
		YHBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'YHBKAzPhotosHigh-Day Group Key Asset',
		CASE YHBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZISCURATED || ''
		END AS 'YHBKAzPhotosHigh-is Curated',
		CASE YHBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZTYPE || ''
		END AS 'YHBKAzPhotosHigh-Type',
		CASE YHBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZKIND || ''
		END AS 'YHBKAzPhotosHigh-Kind',
		CASE YHBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'YHBKAzPhotosHigh-Category',
		CASE YHBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'YHBKAzPhotosHigh-Visibility State',
		CASE YHBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZMOOD || ''
		END AS 'YHBKAzPhotosHigh-Mood',
		CASE YHBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'YHBKAzPhotosHigh-Enrichment State',
		YHBKAzPhotosHigh.ZENRICHMENTVERSION AS 'YHBKAzPhotosHigh-Enrichment Version',
		YHBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'YHBKAzPhotosHigh-Highlight Version',
		z3SuggBKA.Z_3KEYASSETS AS 'z3SuggBKA-3KeyAssets = zAsset-zPK',
		z3SuggBKA.Z_55SUGGESTIONSBEINGKEYASSETS AS 'z3SuggBKA-55SuggBeingKeyAssets = zSugg-zPK',
		SBKAzSugg.Z_PK AS 'SBKAzSugg-zPK',
		SBKAzSugg.ZUUID AS 'SBKAzSugg-UUID',
		DateTime(SBKAzSugg.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Start Date',
		CASE SBKAzSugg.ZSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZSTATE || ''
		END AS 'SBKAzSugg-State',
		CASE SBKAzSugg.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZFEATUREDSTATE || ''
		END AS 'SBKAzSugg-Featured State',
		CASE SBKAzSugg.ZNOTIFICATIONSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZNOTIFICATIONSTATE || ''
		END AS 'SBKAzSugg-Notification State',
		DateTime(SBKAzSugg.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Creation Date',
		DateTime(SBKAzSugg.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-End Date',
		DateTime(SBKAzSugg.ZACTIVATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Activation Date',
		DateTime(SBKAzSugg.ZEXPUNGEDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Expunge Date',
		DateTime(SBKAzSugg.ZRELEVANTUNTILDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Relevant Until Date',
		SBKAzSugg.ZTITLE AS 'SBKAzSugg-Title',
		SBKAzSugg.ZSUBTITLE AS 'SBKAzSugg-Sub Title',
		SBKAzSugg.ZCACHEDCOUNT AS 'SBKAzSugg-Cached Count',
		SBKAzSugg.ZCACHEDPHOTOSCOUNT AS 'SBKAzSugg-Cahed Photos Count',
		SBKAzSugg.ZCACHEDVIDEOSCOUNT AS 'SBKAzSugg-Cached Videos Count',
		CASE SBKAzSugg.ZTYPE
			WHEN 5 THEN '5-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZTYPE || ''
		END AS 'SBKAzSugg-Type',
		CASE SBKAzSugg.ZSUBTYPE
			WHEN 501 THEN '501-StillTesting'
			WHEN 502 THEN '502-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZSUBTYPE || ''
		END AS 'SBKAzSugg-Sub Type',
		SBKAzSugg.ZVERSION AS 'SBKAzSugg-Version',
		CASE SBKAzSugg.ZCLOUDLOCALSTATE
			WHEN 0 THEN 'Suggestion Not Synced with Cloud-0'
			WHEN 1 THEN 'Suggestion Synced with Cloud-1'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZCLOUDLOCALSTATE || ''
		END AS 'SBKAzSugg-Cloud Local State',
		CASE SBKAzSugg.ZCLOUDDELETESTATE
			WHEN 0 THEN 'Suggestion Not Deleted-0'
			WHEN 1 THEN 'Suggestion Deleted-1'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZCLOUDDELETESTATE || ''
		END AS 'SBKAzSugg-Cloud Delete State',
		z3SuggBRA.Z_3REPRESENTATIVEASSETS1 AS 'z3SuggBRA-3RepAssets1',
		z3SuggBRA.Z_55SUGGESTIONSBEINGREPRESENTATIVEASSETS AS 'z3SuggBRA-55SuggBeingRepAssets',
		SBRAzSugg.Z_PK AS 'SBRAzSugg-zPK',
		SBRAzSugg.ZUUID AS 'SBRAzSugg-UUID',
		DateTime(SBRAzSugg.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Start Date',
		CASE SBRAzSugg.ZSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZSTATE || ''
		END AS 'SBRAzSugg-State',
		CASE SBRAzSugg.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZFEATUREDSTATE || ''
		END AS 'SBRAzSugg-Featured State',
		CASE SBRAzSugg.ZNOTIFICATIONSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZNOTIFICATIONSTATE || ''
		END AS 'SBRAzSugg-Notification State',
		DateTime(SBRAzSugg.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Creation Date',
		DateTime(SBRAzSugg.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-End Date',
		DateTime(SBRAzSugg.ZACTIVATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Activation Date',
		DateTime(SBRAzSugg.ZEXPUNGEDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Expunge Date',
		DateTime(SBRAzSugg.ZRELEVANTUNTILDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Relevant Until Date',
		SBRAzSugg.ZTITLE AS 'SBRAzSugg-Title',
		SBRAzSugg.ZSUBTITLE AS 'SBRAzSugg-Sub Title',
		SBRAzSugg.ZCACHEDCOUNT AS 'SBRAzSugg-Cached Count',
		SBRAzSugg.ZCACHEDPHOTOSCOUNT AS 'SBRAzSugg-Cahed Photos Count',
		SBRAzSugg.ZCACHEDVIDEOSCOUNT AS 'SBRAzSugg-Cached Videos Count',
		CASE SBRAzSugg.ZTYPE
			WHEN 5 THEN '5-StillTesting'
			ELSE 'StillTesting-New-Value!: ' || SBRAzSugg.ZTYPE || ''
		END AS 'SBRAzSugg-Type',
		CASE SBRAzSugg.ZSUBTYPE
			WHEN 501 THEN '501-StillTesting'
			WHEN 502 THEN '502-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZSUBTYPE || ''
		END AS 'SBRAzSugg-Sub Type',
		SBRAzSugg.ZVERSION AS 'SBRAzSugg-Version',
		CASE SBRAzSugg.ZCLOUDLOCALSTATE
			WHEN 0 THEN 'Suggestion Not Synced with Cloud-0'
			WHEN 1 THEN 'Suggestion Synced with Cloud-1'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZCLOUDLOCALSTATE || ''
		END AS 'SBRAzSugg-Cloud Local State',
		CASE SBRAzSugg.ZCLOUDDELETESTATE
			WHEN 0 THEN 'Suggestion Not Deleted-0'
			WHEN 1 THEN 'Suggestion Deleted-1'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZCLOUDDELETESTATE || ''
		END AS 'SBRAzSugg-Cloud Delete State',	
		zAsset.ZHIGHLIGHTVISIBILITYSCORE AS 'zAsset-Highlight Visibility Score',
		zMedAnlyAstAttr.ZMEDIAANALYSISVERSION AS 'zMedAnlyAstAttr-Media Analysis Version',
		zMedAnlyAstAttr.ZAUDIOCLASSIFICATION AS 'zMedAnlyAstAttr-Audio Classification',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Duration Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Start Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONVALUE AS 'zMedAnlyAstAttr-Best Video Range Duration Value',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTVALUE AS 'zMedAnlyAstAttr-Best Video Range Start Value',
		zMedAnlyAstAttr.ZPACKEDBESTPLAYBACKRECT AS 'zMedAnlyAstAttr-Packed Best Playback Rect',
		zMedAnlyAstAttr.ZACTIVITYSCORE AS 'zMedAnlyAstAttr-Activity Score',
		zMedAnlyAstAttr.ZVIDEOSCORE AS 'zMedAnlyAstAttr-Video Score',
		zMedAnlyAstAttr.ZAUTOPLAYSUGGESTIONSCORE AS 'zMedAnlyAstAttr-AutoPlay Suggestion Score',
		zMedAnlyAstAttr.ZBLURRINESSSCORE AS 'zMedAnlyAstAttr-Blurriness Score',
		zMedAnlyAstAttr.ZEXPOSURESCORE AS 'zMedAnlyAstAttr-Exposure Score',
		zAssetAnalyState.ZASSETUUID AS 'zAssetAnalyState-Asset UUID-4TableStart',
		zAssetAnalyState.ZANALYSISSTATE AS 'zAssetAnalyState-Analyisis State',
		zAssetAnalyState.ZWORKERFLAGS AS 'zAssetAnalyState-Worker Flags',
		zAssetAnalyState.ZWORKERTYPE AS 'zAssetAnalyState-Worker Type',
		DateTime(zAssetAnalyState.ZIGNOREUNTILDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Ignore Until Date',
		DateTime(zAssetAnalyState.ZLASTIGNOREDDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Last Ignored Date',
		DateTime(zAssetAnalyState.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Sort Token',
		zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',
		zCompAssetAttr.ZBEHAVIORALSCORE AS 'zCompAssetAttr-Behavioral Score',
		zCompAssetAttr.ZFAILURESCORE AS 'zCompAssetAttr-Failure Score zCompAssetAttr',
		zCompAssetAttr.ZHARMONIOUSCOLORSCORE AS 'zCompAssetAttr-Harmonious Color Score',
		zCompAssetAttr.ZIMMERSIVENESSSCORE AS 'zCompAssetAttr-Immersiveness Score',
		zCompAssetAttr.ZINTERACTIONSCORE AS 'zCompAssetAttr-Interaction Score',
		zCompAssetAttr.ZINTERESTINGSUBJECTSCORE AS 'zCompAssetAttr-Intersting Subject Score',
		zCompAssetAttr.ZINTRUSIVEOBJECTPRESENCESCORE AS 'zCompAssetAttr-Intrusive Object Presence Score',
		zCompAssetAttr.ZLIVELYCOLORSCORE AS 'zCompAssetAttr-Lively Color Score',
		zCompAssetAttr.ZLOWLIGHT AS 'zCompAssetAttr-Low Light',
		zCompAssetAttr.ZNOISESCORE AS 'zCompAssetAttr-Noise Score',
		zCompAssetAttr.ZPLEASANTCAMERATILTSCORE AS 'zCompAssetAttr-Pleasant Camera Tilt Score',
		zCompAssetAttr.ZPLEASANTCOMPOSITIONSCORE AS 'zCompAssetAttr-Pleasant Composition Score',
		zCompAssetAttr.ZPLEASANTLIGHTINGSCORE AS 'zCompAssetAttr-Pleasant Lighting Score',
		zCompAssetAttr.ZPLEASANTPATTERNSCORE AS 'zCompAssetAttr-Pleasant Pattern Score',
		zCompAssetAttr.ZPLEASANTPERSPECTIVESCORE AS 'zCompAssetAttr-Pleasant Perspective Score',
		zCompAssetAttr.ZPLEASANTPOSTPROCESSINGSCORE AS 'zCompAssetAttr-Pleasant Post Processing Score',
		zCompAssetAttr.ZPLEASANTREFLECTIONSSCORE AS 'zCompAssetAttr-Pleasant Reflection Score',
		zCompAssetAttr.ZPLEASANTSYMMETRYSCORE AS 'zCompAssetAttrPleasant Symmetry Score',
		zCompAssetAttr.ZSHARPLYFOCUSEDSUBJECTSCORE AS 'zCompAssetAttr-Sharply Focused Subject Score',
		zCompAssetAttr.ZTASTEFULLYBLURREDSCORE AS 'zCompAssetAttr-Tastfully Blurred Score',
		zCompAssetAttr.ZWELLCHOSENSUBJECTSCORE AS 'zCompAssetAttr-Well Chosen Subject Score',
		zCompAssetAttr.ZWELLFRAMEDSUBJECTSCORE AS 'zCompAssetAttr-Well Framed Subject Score',
		zCompAssetAttr.ZWELLTIMEDSHOTSCORE AS 'zCompAssetAttr-Well Timeed Shot Score',
		zCldRes.ZASSETUUID AS 'zCldRes-Asset UUID-4TableStart',
		zCldRes.ZCLOUDLOCALSTATE AS 'zCldRes-Cloud Local State',
		zCldRes.ZFILESIZE AS 'zCldRes-File Size',
		zCldRes.ZHEIGHT AS 'zCldRes-Height',
		zCldRes.ZISAVAILABLE AS 'zCldRes-Is Available',
		zCldRes.ZISLOCALLYAVAILABLE AS 'zCldRes-Is Locally Available',
		zCldRes.ZPREFETCHCOUNT AS 'zCldRes-Prefetch Count',
		zCldRes.ZSOURCETYPE AS 'zCldRes-Source Type',
		zCldRes.ZTYPE AS 'zCldRes-Type',
		zCldRes.ZWIDTH AS 'zCldRes-Width',
		zCldRes.ZDATECREATED AS 'zCldRes-Date Created',
		zCldRes.ZLASTONDEMANDDOWNLOADDATE AS 'zCldRes-Last OnDemand Download Date',
		zCldRes.ZLASTPREFETCHDATE AS 'zCldRes-Last Prefetch Date',
		zCldRes.ZPRUNEDAT AS 'zCldRes-Prunedat',
		zCldRes.ZFILEPATH AS 'zCldRes-File Path',
		zCldRes.ZFINGERPRINT AS 'zCldRes-Fingerprint',
		zCldRes.ZITEMIDENTIFIER AS 'zCldRes-Item ID',
		zCldRes.ZUNIFORMTYPEIDENTIFIER AS 'zCldRes-UniID',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
		zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
		zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
		zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
		zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
		zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
		zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
		zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',
		zAlbumList.Z_PK AS 'zAlbumList-zPK= Album List Key',
		zAlbumList.Z_ENT AS 'zAlbumList-zENT',
		zAlbumList.Z_OPT AS 'zAlbumList-zOPT',
		zAlbumList.ZIDENTIFIER AS 'zAlbumList-ID Key',
		zAlbumList.ZUUID AS 'zAlbumList-UUID',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAsset.Z_ENT AS 'zAsset-zENT',
		zAsset.Z_OPT AS 'zAsset-zOPT',
		zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
		zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
		zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
		zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZMOMENTSHARE AS 'zAsset-Moment Share Key= zShare-zPK',
		zAsset.ZMOMENT AS 'zAsset-zMoment Key= zMoment-zPK',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZHIGHLIGHTBEINGASSETS AS 'zAsset-Highlight Being Assets-HBA Key',
		zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Highlight Being Extended Assets-HBEA Key',
		zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Highligh Being Summary Assets-HBSA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS AS 'zAsset-Day Group Highlight Being Assets-DGHBA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key',
		zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
		zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
		zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
		zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
		zAssetAnalyState.Z_PK AS 'zAssetAnalyState-zPK',
		zAssetAnalyState.Z_ENT AS 'zAssetAnalyState-zEnt',
		zAssetAnalyState.Z_OPT AS 'zAssetAnalyState-zOpt',
		zAssetAnalyState.ZASSET AS 'zAssetAnalyState-Asset= zAsset-zPK',
		zAssetAnalyState.ZASSETUUID AS 'zAssetAnalyState-Asset UUID',
		zAssetDes.Z_PK AS 'zAssetDes-zPK',
		zAssetDes.Z_ENT AS 'zAssetDes-zENT',
		zAssetDes.Z_OPT AS 'zAssetDes-zOPT',
		zAssetDes.ZASSETATTRIBUTES AS 'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK',
		zCldFeedEnt.Z_PK AS 'zCldFeedEnt-zPK= zCldShared keys',
		zCldFeedEnt.Z_ENT AS 'zCldFeedEnt-zENT',
		zCldFeedEnt.Z_OPT AS 'zCldFeedEnt-zOPT',
		zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID',
		zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID',
		zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID',
		zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
		zCldMast.Z_ENT AS 'zCldMast-zENT',
		zCldMast.Z_OPT AS 'zCldMast-zOPT',
		zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
		zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
		CMzCldMastMedData.Z_OPT AS 'CMzCldMastMedData-zOPT',
		CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
		AAAzCldMastMedData.Z_OPT AS 'AAAzCldMastMedData-zOPT',
		AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
		AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
		zCldRes.Z_PK AS 'zCldRes-zPK',
		zCldRes.Z_ENT AS 'zCldRes-zENT',
		zCldRes.Z_OPT AS 'zCldRes-zOPT',
		zCldRes.ZASSET AS 'zCldRes-Asset= zAsset-zPK',
		zCldRes.ZCLOUDMASTER AS 'zCldRes-Cloud Master= zCldMast-zPK',
		zCldRes.ZASSETUUID AS 'zCldRes-Asset UUID',
		zCldShareAlbumInvRec.Z_PK AS 'zCldShareAlbumInvRec-zPK',
		zCldShareAlbumInvRec.Z_ENT AS 'zCldShareAlbumInvRec-zEnt',
		zCldShareAlbumInvRec.Z_OPT AS 'zCldShareAlbumInvRec-zOpt',
		zCldShareAlbumInvRec.ZALBUM AS 'zCldShareAlbumInvRec-Album Key',
		zCldShareAlbumInvRec.Z_FOK_ALBUM AS 'zCldShareAlbumInvRec-FOK Album Key',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
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
		zCompAssetAttr.Z_PK AS 'zCompAssetAttr-zPK',
		zCompAssetAttr.Z_ENT AS 'zCompAssetAttr-zEnt',
		zCompAssetAttr.Z_OPT AS 'zCompAssetAttr-zOpt',
		zCompAssetAttr.ZASSET AS 'zCompAssetAttr-Asset Key',
		zDetFace.Z_PK AS 'zDetFace-zPK',
		zDetFace.Z_ENT AS 'zDetFace-zEnt',
		zDetFace.Z_OPT AS 'zDetFace.zOpt',
		zDetFace.ZASSET AS 'zDetFace-Asset= zAsset-zPK or Asset Containing Face',
		zDetFace.ZPERSON AS 'zDetFace-Person= zPerson-zPK',
		zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',
		zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',
		zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
		zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',
		zDetFace.ZUUID AS 'zDetFace-UUID',
		zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
		zDetFaceGroup.Z_ENT AS 'zDetFaceGroup-zENT',
		zDetFaceGroup.Z_OPT AS 'zDetFaceGroup-zOPT',
		zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
		zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
		zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
		zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',
		zDetFacePrint.Z_ENT AS 'zDetFacePrint-zEnt',
		zDetFacePrint.Z_OPT AS 'zDetFacePrint-zOpt',
		zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
		zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
		zExtAttr.Z_ENT AS 'zExtAttr-zENT',
		zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
		zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
		zFaceCrop.Z_PK AS 'zFaceCrop-zPK',
		zFaceCrop.Z_ENT AS 'zFaceCrop-zEnt',
		zFaceCrop.Z_OPT AS 'zFaceCrop-zOpt',
		zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
		zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',
		zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',
		zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
		zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
		zGenAlbum.Z_PK AS 'zGenAlbum-zPK=26AlbumLists= 26Albums',
		zGenAlbum.Z_ENT AS 'zGenAlbum-zENT',
		zGenAlbum.Z_OPT AS 'zGenAlbum-zOpt',
		zGenAlbum.ZKEYASSET AS 'zGenAlbum-Key Asset-Key zAsset-zPK',
		zGenAlbum.ZSECONDARYKEYASSET AS 'zGenAlbum-Secondary Key Asset',
		zGenAlbum.ZTERTIARYKEYASSET AS 'zGenAlbum-Tertiary Key Asset',
		zGenAlbum.ZCUSTOMKEYASSET AS 'zGenAlbum-Custom Key Asset',
		zGenAlbum.ZPARENTFOLDER AS 'zGenAlbum-Parent Folder Key= zGenAlbum-zPK',
		zGenAlbum.Z_FOK_PARENTFOLDER AS 'zGenAlbum-FOK Parent Folder',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud_GUID = store.cloudphotodb',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',
		zIntResou.Z_PK AS 'zIntResou-zPK',
		zIntResou.Z_ENT AS 'zIntResou-zENT',
		zIntResou.Z_OPT AS 'zIntResou-zOPT',
		zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
		zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
		zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
		zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
		zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK',
		zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
		zPerson.Z_ENT AS 'zPerson-zEnt',
		zPerson.Z_OPT AS 'zPerson-zOpt',
		zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
		zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
		zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
		zSceneP.Z_PK AS 'zSceneP-zPK',
		zSceneP.Z_ENT AS 'zSceneP-zENT',
		zSceneP.Z_OPT AS 'zSceneP-zOPT',
		zShare.Z_PK AS 'zShare-zPK',
		zShare.Z_ENT AS 'zShare-zENT',
		zShare.Z_OPT AS 'zShare-zOPT',
		zShare.ZUUID AS 'zShare-UUID',
		SPLzShare.ZUUID AS 'SPLzShare-UUID',
		zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID = store.cloudphotodb',
		zSharePartic.Z_PK AS 'zSharePartic-zPK',
		zSharePartic.Z_ENT AS 'zSharePartic-zENT',
		zSharePartic.Z_OPT AS 'zSharePartic-zOPT',
		zSharePartic.ZSHARE AS 'zSharePartic-Share Key= zShare-zPK',
		zSharePartic.ZUUID AS 'zSharePartic-UUID',
		zUnmAdj.Z_PK AS 'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key',
		zUnmAdj.Z_OPT AS 'zUnmAdj-zOPT',
		zUnmAdj.Z_ENT AS 'zUnmAdj-zENT',
		zUnmAdj.ZASSETATTRIBUTES AS 'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK',
		zUnmAdj.ZUUID AS 'zUnmAdj-UUID',
		zUnmAdj.ZOTHERADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Other Adjustments Fingerprint',
		zUnmAdj.ZSIMILARTOORIGINALADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Similar to Orig Adjustments Fingerprint',
		z25AlbumLists.Z_25ALBUMS AS 'z25AlbumList-25Albums= zGenAlbum-zPK',
		z25AlbumLists.Z_2ALBUMLISTS AS 'z25AlbumList-Album List Key',
		z25AlbumLists.Z_FOK_25ALBUMS AS 'z25AlbumList-FOK25Albums Key',
		z26Assets.Z_26ALBUMS AS 'z26Assets-26Albums= zGenAlbum-zPK',
		z26Assets.Z_3ASSETS AS 'z26Assets-3Asset Key= zAsset-zPK in the Album',
		z26Assets.Z_FOK_3ASSETS AS 'z26Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT
			LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
			LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
			LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
			LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
			LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
			LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
			LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDRESOURCE zCldRes ON zCldRes.ZCLOUDMASTER = zCldMast.Z_PK
			LEFT JOIN ZASSETANALYSISSTATE zAssetAnalyState ON zAssetAnalyState.ZASSET = zAsset.Z_PK
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
			LEFT JOIN ZCOMPUTEDASSETATTRIBUTES zCompAssetAttr ON zCompAssetAttr.Z_PK = zAsset.ZCOMPUTEDATTRIBUTES
			LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
			LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
			LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
			LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.ZSHARE = SPLzShare.Z_PK
			LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
			LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
			LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
			LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
			LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
			LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
			LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
			LEFT JOIN Z_3MEMORIESBEINGCURATEDASSETS z3MemoryBCAs ON zAsset.Z_PK = z3MemoryBCAs.Z_3CURATEDASSETS
			LEFT JOIN ZMEMORY zMemory ON z3MemoryBCAs.Z_40MEMORIESBEINGCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGEXTENDEDCURATEDASSETS z3MemoryBECAs ON zAsset.Z_PK = z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AND z3MemoryBECAs.Z_40MEMORIESBEINGEXTENDEDCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGMOVIECURATEDASSETS z3MemoryBMCAs ON zAsset.Z_PK = z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AND z3MemoryBMCAs.Z_40MEMORIESBEINGMOVIECURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGREPRESENTATIVEASSETS z3MemoryBRAs ON zAsset.Z_PK = z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AND z3MemoryBRAs.Z_40MEMORIESBEINGREPRESENTATIVEASSETS = zMemory.Z_PK
			LEFT JOIN ZMOMENT zMoment ON zMoment.Z_PK = zAsset.ZMOMENT
			LEFT JOIN ZMOMENTLIST YearzMomentList ON YearzMomentList.Z_PK = zMoment.ZYEARMOMENTLIST
			LEFT JOIN ZMOMENTLIST MegaYMzMomentList ON MegaYMzMomentList.Z_PK = zMoment.ZMEGAMOMENTLIST
			LEFT JOIN ZPHOTOSHIGHLIGHT HBAzPhotosHigh ON HBAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT HBEAzPhotosHigh ON HBEAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT HBKAzPhotosHigh ON HBKAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT HBSAzPhotosHigh ON HBSAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT YHBKAzPhotosHigh ON YHBKAzPhotosHigh.Z_PK = zAsset.ZYEARHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT MHBFAzPhotosHigh ON MHBFAzPhotosHigh.Z_PK = zAsset.ZMONTHHIGHLIGHTBEINGFIRSTASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT MHBKAzPhotosHigh ON MHBKAzPhotosHigh.Z_PK = zAsset.ZMONTHHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBAzPhotosHigh ON DGHBAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBEAzPhotosHigh ON DGHBEAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBKAzPhotosHigh ON DGHBKAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBSAzPhotosHigh ON DGHBSAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT YMParzPhotosHigh ON YMParzPhotosHigh.Z_PK = HBAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT
			LEFT JOIN ZPHOTOSHIGHLIGHT YearParzPhotosHigh ON YearParzPhotosHigh.Z_PK = YMParzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT
			LEFT JOIN ZPHOTOSHIGHLIGHT DGParzPhotosHigh ON DGParzPhotosHigh.Z_PK = HBAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT
			LEFT JOIN Z_3SUGGESTIONSBEINGKEYASSETS z3SuggBKA ON z3SuggBKA.Z_3KEYASSETS = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBKAzSugg ON SBKAzSugg.Z_PK = z3SuggBKA.Z_55SUGGESTIONSBEINGKEYASSETS
			LEFT JOIN Z_3SUGGESTIONSBEINGREPRESENTATIVEASSETS z3SuggBRA ON z3SuggBRA.Z_3REPRESENTATIVEASSETS1 = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBRAzSugg ON SBRAzSugg.Z_PK = z3SuggBRA.Z_55SUGGESTIONSBEINGREPRESENTATIVEASSETS
		ORDER BY zAsset.ZADDEDDATE
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
							row[268], row[269], row[270], row[271], row[272], row[273], row[274], row[275],
							row[276], row[277], row[278], row[279], row[280], row[281], row[282], row[283],
							row[284], row[285], row[286], row[287], row[288], row[289], row[290], row[291],
							row[292], row[293], row[294], row[295], row[296], row[297], row[298], row[299],
							row[300], row[301], row[302], row[303], row[304], row[305], row[306], row[307],
							row[308], row[309], row[310], row[311], row[312], row[313], row[314], row[315],
							row[316], row[317], row[318], row[319], row[320], row[321], row[322], row[323],
							row[324], row[325], row[326], row[327], row[328], row[329], row[330], row[331],
							row[332], row[333], row[334], row[335], row[336], row[337], row[338], row[339],
							row[340], row[341], row[342], row[343], row[344], row[345], row[346], row[347],
							row[348], row[349], row[350], row[351], row[352], row[353], row[354], row[355],
							row[356], row[357], row[358], row[359], row[360], row[361], row[362], row[363],
							row[364], row[365], row[366], row[367], row[368], row[369], row[370], row[371],
							row[372], row[373], row[374], row[375], row[376], row[377], row[378], row[379],
							row[380], row[381], row[382], row[383], row[384], row[385], row[386], row[387],
							row[388], row[389], row[390], row[391], row[392], row[393], row[394], row[395],
							row[396], row[397], row[398], row[399], row[400], row[401], row[402], row[403],
							row[404], row[405], row[406], row[407], row[408], row[409], row[410], row[411],
							row[412], row[413], row[414], row[415], row[416], row[417], row[418], row[419],
							row[420], row[421], row[422], row[423], row[424], row[425], row[426], row[427],
							row[428], row[429], row[430], row[431], row[432], row[433], row[434], row[435],
							row[436], row[437], row[438], row[439], row[440], row[441], row[442], row[443],
							row[444], row[445], row[446], row[447], row[448], row[449], row[450], row[451],
							row[452], row[453], row[454], row[455], row[456], row[457], row[458], row[459],
							row[460], row[461], row[462], row[463], row[464], row[465], row[466], row[467],
							row[468], row[469], row[470], row[471], row[472], row[473], row[474], row[475],
							row[476], row[477], row[478], row[479], row[480], row[481], row[482], row[483],
							row[484], row[485], row[486], row[487], row[488], row[489], row[490], row[491],
							row[492], row[493], row[494], row[495], row[496], row[497], row[498], row[499],
							row[500], row[501], row[502], row[503], row[504], row[505], row[506], row[507],
							row[508], row[509], row[510], row[511], row[512], row[513], row[514], row[515],
							row[516], row[517], row[518], row[519], row[520], row[521], row[522], row[523],
							row[524], row[525], row[526], row[527], row[528], row[529], row[530], row[531],
							row[532], row[533], row[534], row[535], row[536], row[537], row[538], row[539],
							row[540], row[541], row[542], row[543], row[544], row[545], row[546], row[547],
							row[548], row[549], row[550], row[551], row[552], row[553], row[554], row[555],
							row[556], row[557], row[558], row[559], row[560], row[561], row[562], row[563],
							row[564], row[565], row[566], row[567], row[568], row[569], row[570], row[571],
							row[572], row[573], row[574], row[575], row[576], row[577], row[578], row[579],
							row[580], row[581], row[582], row[583], row[584], row[585], row[586], row[587],
							row[588], row[589], row[590], row[591], row[592], row[593], row[594], row[595],
							row[596], row[597], row[598], row[599], row[600], row[601], row[602], row[603],
							row[604], row[605], row[606], row[607], row[608], row[609], row[610], row[611],
							row[612], row[613], row[614], row[615], row[616], row[617], row[618], row[619],
							row[620], row[621], row[622], row[623], row[624], row[625], row[626], row[627],
							row[628], row[629], row[630], row[631], row[632], row[633], row[634], row[635],
							row[636], row[637], row[638], row[639], row[640], row[641], row[642], row[643],
							row[644], row[645], row[646], row[647], row[648], row[649], row[650], row[651],
							row[652], row[653], row[654], row[655], row[656], row[657], row[658], row[659],
							row[660], row[661], row[662], row[663], row[664], row[665], row[666], row[667],
							row[668], row[669], row[670], row[671], row[672], row[673], row[674], row[675],
							row[676], row[677], row[678], row[679], row[680], row[681], row[682], row[683],
							row[684], row[685], row[686], row[687], row[688], row[689], row[690], row[691],
							row[692], row[693], row[694], row[695], row[696], row[697], row[698], row[699],
							row[700], row[701], row[702], row[703], row[704], row[705], row[706], row[707],
							row[708], row[709], row[710], row[711], row[712], row[713], row[714], row[715],
							row[716], row[717], row[718], row[719], row[720], row[721], row[722], row[723],
							row[724], row[725], row[726], row[727], row[728], row[729], row[730], row[731],
							row[732], row[733], row[734], row[735], row[736], row[737], row[738], row[739],
							row[740], row[741], row[742], row[743], row[744], row[745], row[746], row[747],
							row[748], row[749], row[750], row[751], row[752], row[753], row[754], row[755],
							row[756], row[757], row[758], row[759], row[760], row[761], row[762], row[763],
							row[764], row[765], row[766], row[767], row[768], row[769], row[770], row[771],
							row[772], row[773], row[774], row[775], row[776], row[777], row[778], row[779],
							row[780], row[781], row[782], row[783], row[784], row[785], row[786], row[787],
							row[788], row[789], row[790], row[791], row[792], row[793], row[794], row[795],
							row[796], row[797], row[798], row[799], row[800], row[801], row[802], row[803],
							row[804], row[805], row[806], row[807], row[808], row[809], row[810], row[811],
							row[812], row[813], row[814], row[815], row[816], row[817], row[818], row[819],
							row[820], row[821], row[822], row[823], row[824], row[825], row[826], row[827],
							row[828], row[829], row[830], row[831], row[832], row[833], row[834], row[835],
							row[836], row[837], row[838], row[839], row[840], row[841], row[842], row[843],
							row[844], row[845], row[846], row[847], row[848], row[849], row[850], row[851],
							row[852], row[853], row[854], row[855], row[856], row[857], row[858], row[859],
							row[860], row[861], row[862], row[863], row[864], row[865], row[866], row[867],
							row[868], row[869], row[870], row[871], row[872], row[873], row[874], row[875],
							row[876], row[877], row[878], row[879], row[880], row[881], row[882], row[883],
							row[884], row[885], row[886], row[887], row[888], row[889], row[890], row[891],
							row[892], row[893], row[894], row[895], row[896], row[897], row[898], row[899],
							row[900], row[901], row[902], row[903], row[904], row[905], row[906], row[907],
							row[908], row[909], row[910], row[911], row[912], row[913], row[914], row[915],
							row[916], row[917], row[918], row[919], row[920], row[921], row[922], row[923],
							row[924], row[925], row[926], row[927], row[928], row[929], row[930], row[931],
							row[932], row[933], row[934], row[935], row[936], row[937], row[938], row[939],
							row[940], row[941], row[942], row[943], row[944], row[945], row[946], row[947],
							row[948], row[949], row[950], row[951], row[952], row[953], row[954], row[955],
							row[956], row[957], row[958], row[959], row[960], row[961], row[962], row[963],
							row[964], row[965], row[966], row[967], row[968], row[969], row[970], row[971],
							row[972], row[973], row[974], row[975], row[976], row[977], row[978], row[979],
							row[980], row[981], row[982], row[983], row[984], row[985], row[986], row[987],
							row[988], row[989], row[990], row[991], row[992], row[993], row[994], row[995],
							row[996], row[997], row[998], row[999], row[1000], row[1001], row[1002],
							row[1003], row[1004], row[1005], row[1006], row[1007], row[1008], row[1009],
							row[1010], row[1011], row[1012], row[1013], row[1014], row[1015], row[1016],
							row[1017], row[1018], row[1019], row[1020], row[1021], row[1022], row[1023],
							row[1024], row[1025], row[1026], row[1027], row[1028], row[1029], row[1030],
							row[1031], row[1032], row[1033], row[1034], row[1035], row[1036], row[1037],
							row[1038], row[1039], row[1040], row[1041], row[1042], row[1043], row[1044],
							row[1045], row[1046], row[1047], row[1048], row[1049], row[1050], row[1051],
							row[1052], row[1053], row[1054], row[1055], row[1056], row[1057], row[1058],
							row[1059], row[1060], row[1061], row[1062], row[1063], row[1064], row[1065],
							row[1066], row[1067], row[1068], row[1069], row[1070], row[1071], row[1072],
							row[1073], row[1074], row[1075], row[1076], row[1077], row[1078], row[1079],
							row[1080], row[1081], row[1082], row[1083], row[1084], row[1085], row[1086],
							row[1087], row[1088], row[1089], row[1090], row[1091], row[1092], row[1093],
							row[1094], row[1095], row[1096], row[1097], row[1098], row[1099], row[1100],
							row[1101], row[1102], row[1103], row[1104], row[1105], row[1106], row[1107],
							row[1108], row[1109], row[1110], row[1111], row[1112], row[1113], row[1114],
							row[1115], row[1116], row[1117], row[1118], row[1119], row[1120], row[1121],
							row[1122], row[1123], row[1124], row[1125], row[1126], row[1127], row[1128],
							row[1129], row[1130], row[1131], row[1132], row[1133], row[1134], row[1135],
							row[1136], row[1137], row[1138], row[1139], row[1140], row[1141], row[1142],
							row[1143], row[1144], row[1145], row[1146], row[1147], row[1148], row[1149],
							row[1150], row[1151], row[1152], row[1153], row[1154], row[1155], row[1156],
							row[1157], row[1158], row[1159], row[1160], row[1161], row[1162], row[1163],
							row[1164], row[1165], row[1166], row[1167], row[1168], row[1169], row[1170],
							row[1171], row[1172], row[1173], row[1174], row[1175], row[1176], row[1177],
							row[1178], row[1179], row[1180], row[1181], row[1182], row[1183], row[1184],
							row[1185], row[1186], row[1187], row[1188], row[1189], row[1190], row[1191],
							row[1192], row[1193], row[1194], row[1195], row[1196], row[1197], row[1198],
							row[1199], row[1200], row[1201], row[1202], row[1203], row[1204], row[1205],
							row[1206], row[1207], row[1208], row[1209], row[1210], row[1211], row[1212],
							row[1213], row[1214], row[1215], row[1216], row[1217], row[1218], row[1219],
							row[1220], row[1221], row[1222], row[1223], row[1224], row[1225], row[1226],
							row[1227], row[1228], row[1229], row[1230], row[1231], row[1232], row[1233],
							row[1234], row[1235], row[1236], row[1237], row[1238], row[1239], row[1240],
							row[1241], row[1242], row[1243], row[1244], row[1245], row[1246], row[1247],
							row[1248], row[1249], row[1250], row[1251], row[1252], row[1253], row[1254],
							row[1255], row[1256], row[1257], row[1258], row[1259], row[1260], row[1261],
							row[1262], row[1263], row[1264], row[1265], row[1266], row[1267], row[1268],
							row[1269]))

		data_headers = (('zAsset-Added Date-0', 'datetime'),
						'zAsset- SortToken -CameraRoll-1',
						'zAsset Complete-2',
						'zAsset-zPK-4QueryStart-3',
						'zAddAssetAttr-zPK-4QueryStart-4',
						'zAsset-UUID = store.cloudphotodb-4QueryStart-5',
						'zAddAssetAttr-Master Fingerprint-4TableStart-6',
						'zIntResou-Fingerprint-4TableStart-7',
						'zAsset-Cloud is My Asset-8',
						'zAsset-Cloud is deletable-Asset-9',
						'zAsset-Cloud_Local_State-10',
						'zAsset-Visibility State-11',
						'zExtAttr-Camera Make-12',
						'zExtAttr-Camera Model-13',
						'zExtAttr-Lens Model-14',
						'zExtAttr-Flash Fired-15',
						'zExtAttr-Focal Lenght-16',
						'zAsset-Derived Camera Capture Device-17',
						'zAddAssetAttr-Camera Captured Device-18',
						'zAddAssetAttr-Imported by-19',
						'zCldMast-Imported By-20',
						'zAddAssetAttr-Creator Bundle ID-21',
						'zAddAssetAttr-Imported By Display Name-22',
						'zCldMast-Imported by Bundle ID-23',
						'zCldMast-Imported by Display Name-24',
						'zAsset-Saved Asset Type-25',
						'zAsset-Directory-Path-26',
						'zAsset-Filename-27',
						'zAddAssetAttr- Original Filename-28',
						'zCldMast- Original Filename-29',
						('zAsset-Date Created-30', 'datetime'),
						('zCldMast-Creation Date-31', 'datetime'),
						('zIntResou-CldMst Date Created-32', 'datetime'),
						'zAddAssetAttr-Time Zone Name-33',
						'zAddAssetAttr-Time Zone Offset-34',
						'zAddAssetAttr-Inferred Time Zone Offset-35',
						'zAddAssetAttr-EXIF-String-36',
						('zAsset-Modification Date-37', 'datetime'),
						('zAsset-Last Shared Date-38', 'datetime'),
						'zCldMast-Cloud Local State-39',
						('zCldMast-Import Date-40', 'datetime'),
						('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-41', 'datetime'),
						'zAddAssetAttr-Import Session ID-4QueryStart-42',
						('zAddAssetAttr-Alt Import Image Date-43', 'datetime'),
						'zCldMast-Import Session ID- AirDrop-StillTesting- 4QueryStart-44',
						('zAsset-Cloud Batch Publish Date-45', 'datetime'),
						('zAsset-Cloud Server Publish Date-46', 'datetime'),
						'zAsset-Cloud Download Requests-47',
						'zAsset-Cloud Batch ID-48',
						'zAddAssetAttr-Upload Attempts-49',
						'zAsset-Latitude-50',
						'zExtAttr-Latitude-51',
						'zAsset-Longitude-52',
						'zExtAttr-Longitude-53',
						'zAddAssetAttr-GPS Horizontal Accuracy-54',
						'zAddAssetAttr-Location Hash-55',
						'zAddAssetAttr-Shifted Location Valid-56',
						'zAddAssetAttr-Shifted Location Data-57',
						'zAddAssetAttr-Reverse Location Is Valid-58',
						'zAddAssetAttr-Reverse Location Data-59',
						'ParentzGenAlbum-UUID-4QueryStart-60',
						'zGenAlbum-UUID-4QueryStart-61',
						'ParentzGenAlbum-Cloud GUID-4QueryStart-62',
						'zGenAlbum-Cloud GUID-4QueryStart-63',
						'zCldShareAlbumInvRec-Album GUID-4QueryStart-64',
						'zCldShareAlbumInvRec-Cloud GUID-4QueryStart-65',
						'zGenAlbum-Project Render UUID-4QueryStart-66',
						'ParentzGenAlbum-Cloud-Local-State-4QueryStart-67',
						'zGenAlbum-Cloud_Local_State-4QueryStart-68',
						('ParentzGenAlbum- Creation Date- 4QueryStart-69', 'datetime'),
						('zGenAlbum- Creation Date- 4QueryStart-70', 'datetime'),
						('zGenAlbum- Cloud Creation Date- 4QueryStart-71', 'datetime'),
						('zGenAlbum- Start Date- 4QueryStart-72', 'datetime'),
						('zGenAlbum- End Date- 4QueryStart-73', 'datetime'),
						('zGenAlbum-Cloud Subscription Date- 4QueryStart-74', 'datetime'),
						'ParentzGenAlbum- Title- 4QueryStart-75',
						'zGenAlbum- Title-User&System Applied- 4QueryStart-76',
						'zGenAlbum-Import Session ID-SWY- 4QueryStart-77',
						'zGenAlbum-Creator Bundle ID- 4QueryStart-78',
						'zGenAlbum-zENT- Entity- 4QueryStart-79',
						'ParentzGenAlbum- Kind- 4QueryStart-80',
						'zGenAlbum-Album Kind- 4QueryStart-81',
						'AAAzCldMastMedData-zOPT-82',
						'zAddAssetAttr-Media Metadata Type-83',
						'AAAzCldMastMedData-Data-84',
						'CldMasterzCldMastMedData-zOPT-85',
						'zCldMast-Media Metadata Type-86',
						'CMzCldMastMedData-Data-87',
						'zAsset-Orientation-88',
						'zAddAssetAttr-Original Orientation-89',
						'zAsset-Kind-90',
						'zAsset-Kind-Sub-Type-91',
						'zAddAssetAttr-Cloud Kind Sub Type-92',
						'zAsset-Playback Style-93',
						'zAsset-Playback Variation-94',
						'zAsset-Video Duration-95',
						'zExtAttr-Duration-96',
						'zAsset-Video CP Duration-97',
						'zAddAssetAttr-Video CP Duration Time Scale-98',
						'zAsset-Video CP Visibility State-99',
						'zAddAssetAttr-Video CP Display Value-100',
						'zAddAssetAttr-Video CP Display Time Scale-101',
						'zIntResou-Datastore Class ID-102',
						'zAsset-Cloud Placeholder Kind-103',
						'zIntResou-Local Availability-104',
						'zIntResou-Local Availability Target-105',
						'zIntResou-Cloud Local State-106',
						'zIntResou-Remote Availability-107',
						'zIntResou-Remote Availability Target-108',
						'zIntResou-Transient Cloud Master-109',
						'zIntResou-Side Car Index-110',
						'zIntResou- File ID-111',
						'zIntResou-Version-112',
						'zAddAssetAttr- Original-File-Size-113',
						'zIntResou-Resource Type-114',
						'zIntResou-Datastore Sub-Type-115',
						'zIntResou-Cloud Source Type-116',
						'zIntResou-Data Length-117',
						'zIntResou-Recipe ID-118',
						('zIntResou-Cloud Last Prefetch Date-119', 'datetime'),
						'zIntResou-Cloud Prefetch Count-120',
						('zIntResou- Cloud-Last-OnDemand Download-Date-121', 'datetime'),
						'zAsset-Uniform Type ID-122',
						'zAsset-Original Color Space-123',
						'zCldMast-Uniform_Type_ID-124',
						'zCldMast-Full Size JPEG Source-125',
						'zAsset-HDR Gain-126',
						'zExtAttr-Codec-127',
						'zCldMast-Codec Name-128',
						'zCldMast-Video Frame Rate-129',
						'zCldMast-Placeholder State-130',
						'zAsset-Depth_Type-131',
						'zAsset-Avalanche UUID-4TableStart-132',
						'zAsset-Avalanche_Pick_Type-BurstAsset-133',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-134',
						'zAddAssetAttr-Cloud Recovery State-135',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-136',
						'zAsset-Deferred Processing Needed-137',
						'zAddAssetAttr-Deferred Photo Identifier-4QueryStart-138',
						'zAddAssetAttr-Deferred Processing Candidate Options-139',
						'zAsset-Has Adjustments-Camera-Effects-Filters-140',
						'zUnmAdj-UUID-4TableStart-141',
						'zAsset-Adjustment Timestamp-142',
						'zUnmAdj-Adjustment Timestamp-143',
						'zAddAssetAttr-Editor Bundle ID-144',
						'zUnmAdj-Editor Localized Name-145',
						'zUnmAdj-Adjustment Format ID-146',
						'zAddAssetAttr-Montage-147',
						'zUnmAdj-Adjustment Render Types-148',
						'zUnmAdj-Adjustment Format Version-149',
						'zUnmAdj-Adjustment Base Image Format-150',
						'zAsset-Favorite-151',
						'zAsset-Hidden-152',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-153',
						('zAsset-Trashed Date-154', 'datetime'),
						'zIntResou-Trash State-155',
						('zIntResou-Trashed Date-156', 'datetime'),
						'zAsset-Cloud Delete State-157',
						'zIntResou-Cloud Delete State-158',
						'zAddAssetAttr-PTP Trashed State-159',
						'zIntResou-PTP Trashed State-160',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-4TableStart-161',
						'zMedAnlyAstAttr-Media Analysis Timestamp-162',
						('zAsset-Analysis State Modification Date-163', 'datetime'),
						'zAddAssetAttr- Pending View Count-164',
						'zAddAssetAttr- View Count-165',
						'zAddAssetAttr- Pending Play Count-166',
						'zAddAssetAttr- Play Count-167',
						'zAddAssetAttr- Pending Share Count-168',
						'zAddAssetAttr- Share Count-169',
						'zAddAssetAttr-Allowed for Analysis-170',
						'zAddAssetAttr-Scene Analysis Version-171',
						'zAddAssetAttr-Scene Analysis Timestamp-172',
						'zAddAssetAttr-Destination Asset Copy State-173',
						'zAddAssetAttr-Variation Suggestions States-174',
						'zAsset-High Frame Rate State-175',
						'zAsset-Video Key Frame Time Scale-176',
						'zAsset-Video Key Frame Value-177',
						'zExtAttr-ISO-178',
						'zExtAttr-Metering Mode-179',
						'zExtAttr-Sample Rate-180',
						'zExtAttr-Track Format-181',
						'zExtAttr-White Balance-182',
						'zExtAttr-Aperture-183',
						'zExtAttr-BitRate-184',
						'zExtAttr-Exposure Bias-185',
						'zExtAttr-Frames Per Second-186',
						'zExtAttr-Shutter Speed-187',
						'zAsset-Height-188',
						'zAddAssetAttr-Original Height-189',
						'zIntResou-Unoriented Height-190',
						'zAsset-Width-191',
						'zAddAssetAttr-Original Width-192',
						'zIntResou-Unoriented Width-193',
						'zShare-Thumbnail Image Data-194',
						'SPLzShare-Thumbnail Image Data-195',
						'zAsset-Thumbnail Index-196',
						'zAddAssetAttr-Embedded Thumbnail Height-197',
						'zAddAssetAttr-Embedded Thumbnail Length-198',
						'zAddAssetAttr-Embedded Thumbnail Offset-199',
						'zAddAssetAttr-Embedded Thumbnail Width-200',
						'zAsset-Packed Acceptable Crop Rect-201',
						'zAsset-Packed Badge Attributes-202',
						'zAsset-Packed Preferred Crop Rect-203',
						'zAsset-Curation Score-204',
						'zAsset-Camera Processing Adjustment State-205',
						'zAsset-Depth Type-206',
						'zAddAssetAttr-Orig Resource Choice-207',
						'zAddAssetAttr-Spatial Over Capture Group ID-208',
						'zAddAssetAttr-Place Annotation Data-209',
						'zAddAssetAttr-Distance Identity-210',
						'zAddAssetAttr-Edited IPTC Attributes-211',
						'zAssetDes-Long Description-212',
						'zAddAssetAttr-Asset Description-213',
						'zAddAssetAttr-Title-Comments via Cloud Website-214',
						'zAddAssetAttr-Accessibility Description-215',
						'zAddAssetAttr-Photo Stream Tag ID-216',
						('zCldFeedEnt-Entry Date-217', 'datetime'),
						'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-218',
						'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-219',
						'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-220',
						'zCldFeedEnt-Entry Priority Number-221',
						'zCldFeedEnt-Entry Type Number-222',
						'zCldSharedComment-Cloud GUID-4TableStart-223',
						('zCldSharedComment-Date-224', 'datetime'),
						('zCldSharedComment-Comment Client Date-225', 'datetime'),
						('zAsset-Cloud Last Viewed Comment Date-226', 'datetime'),
						'zCldSharedComment-Type-227',
						'zCldSharedComment-Comment Text-228',
						'zCldSharedComment-Commenter Hashed Person ID-229',
						'zCldSharedComment-Batch Comment-230',
						'zCldSharedComment-Is a Caption-231',
						'zAsset-Cloud Has Comments by Me-232',
						'zCldSharedComment-Is My Comment-233',
						'zCldSharedComment-Is Deletable-234',
						'zAsset-Cloud Has Comments Conversation-235',
						'zAsset-Cloud Has Unseen Comments-236',
						'zCldSharedComment-Liked-237',
						'zAddAssetAttr-Share Type-238',
						'zShare-UUID-CMM-4TableStart-239',
						'SPLzShare-UUID-SPL-4TableStart-240',
						'zShare-zENT-CMM-241',
						'SPLzShare-zENT-SPL-242',
						'zShare-Status-CMM-243',
						'SPLzShare-Status-SPL-244',
						'zShare-Scope Type-CMM-245',
						'SPLzShare-Scope Type-SPL-246',
						'zShare-Local Publish State-CMM-247',
						'SPLzShare-Local Publish State-SPL-248',
						'zShare-Public Permission-CMM-249',
						'SPLzShare-Public Permission-SPL-250',
						'zShare-Originating Scope ID-CMM-251',
						'SPLzShare-Originating Scope ID-SPL-252',
						'zShare-Scope ID-CMM-253',
						'SPLzShare-Scope ID-SPL-254',
						'zShare-Title-CMM-255',
						'SPLzShare-Title-SPL-256',
						'zShare-Share URL-CMM-257',
						'SPLzShare-Share URL-SPL-258',
						('zShare-Creation Date-CMM-259', 'datetime'),
						('SPLzShare-Creation Date-SPL-260', 'datetime'),
						('zShare-Start Date-CMM-261', 'datetime'),
						('SPLzShare-Start Date-SPL-262', 'datetime'),
						('zShare-End Date-CMM-263', 'datetime'),
						('SPLzShare-End Date-SPL-264', 'datetime'),
						('zShare-Expiry Date-CMM-265', 'datetime'),
						('SPLzShare-Expiry Date-SPL-266', 'datetime'),
						'zShare-Asset Count-CMM-267',
						'SPLzShare-Asset Count-SPL-268',
						'zShare-Photos Count-CMM-269',
						'SPLzShare-Photos Count-CMM-SPL-270',
						'zShare-Uploaded Photos Count-CMM-271',
						'SPLzShare-Uploaded Photos Count-SPL-272',
						'zShare-Videos Count-CMM-273',
						'SPLzShare-Videos Count-SPL-274',
						'zShare-Uploaded Videos Count-CMM-275',
						'SPLzShare-Uploaded Videos Count-SPL-276',
						'zShare-Force Sync Attempted-CMM-277',
						'SPLzShare-Force Sync Attempted-SPL-278',
						'zShare-Should Notify On Upload Completion-CMM-279',
						'SPLzShare-Should Notify On Upload Completion-SPL-280',
						'zShare-Trashed State-CMM-281',
						'SPLzShare-Trashed State-SPL-282',
						'zShare-Cloud Delete State-CMM-283',
						'SPLzShare-Cloud Delete State-SPL-284',
						'zShare-Should Ignor Budgets-CMM-285',
						'SPLzShare-Should Ignor Budgets-SPL-286',
						'zSharePartic-UUID-4TableStart-287',
						'SPLzSharePartic-UUID-4TableStart-288',
						'zSharePartic-Acceptance Status-289',
						'SPLzSharePartic-Acceptance Status-290',
						'zSharePartic-Is Current User-291',
						'SPLzSharePartic-Is Current User-292',
						'zSharePartic-Role-293',
						'SPLzSharePartic-Role-294',
						'zSharePartic-Premission-295',
						'SPLzSharePartic-Premission-296',
						'zSharePartic-User ID-297',
						'SPLzSharePartic-User ID-298',
						'SPLzSharePartic-zPK-4TableStart-299',
						'zSharePartic-zPK-4TableStart-300',
						'zSharePartic-Email Address-301',
						'SPLzSharePartic-Email Address-302',
						'zSharePartic-Phone Number-303',
						'SPLzSharePartic-Phone Number-304',
						'ParentzGenAlbum-UUID-4TableStart-305',
						'zGenAlbum-UUID-4TableStart-306',
						'ParentzGenAlbum-Cloud GUID-4TableStart-307',
						'zGenAlbum-Cloud GUID-4TableStart-308',
						'zCldShareAlbumInvRec-Album GUID-4TableStart-309',
						'zCldShareAlbumInvRec-Cloud GUID-4TableStart-310',
						'zGenAlbum-Project Render UUID-4TableStart-311',
						'zAlbumList-Needs Reordering Number-312',
						'zGenAlbum-zENT- Entity-313',
						'ParentzGenAlbum-Kind-314',
						'zGenAlbum-Album Kind-315',
						'ParentzGenAlbum-Cloud-Local-State-316',
						'zGenAlbum-Cloud_Local_State-317',
						'ParentzGenAlbum- Title-318',
						'zGenAlbum- Title-User&System Applied-319',
						'zGenAlbum-Import Session ID-SWY-320',
						'zGenAlbum-Creator Bundle ID-321',
						('ParentzGenAlbum-Creation Date-322', 'datetime'),
						('zGenAlbum-Creation Date-323', 'datetime'),
						('zGenAlbum-Cloud Creation Date-324', 'datetime'),
						('zGenAlbum-Start Date-325', 'datetime'),
						('zGenAlbum-End Date-326', 'datetime'),
						('zGenAlbum-Cloud Subscription Date-327', 'datetime'),
						'ParentzGenAlbum-Pending Items Count-328',
						'zGenAlbum-Pending Items Count-329',
						'ParentzGenAlbum-Pending Items Type-330',
						'zGenAlbum-Pending Items Type-331',
						'zGenAlbum- Cached Photos Count-332',
						'zGenAlbum- Cached Videos Count-333',
						'zGenAlbum- Cached Count-334',
						'ParentzGenAlbum-Sync Event Order Key-335',
						'zGenAlbum-Sync Event Order Key-336',
						'zGenAlbum-Has Unseen Content-337',
						'zGenAlbum-Unseen Asset Count-338',
						'zGenAlbum-is Owned-339',
						'zGenAlbum-Cloud Relationship State-340',
						'zGenAlbum-Cloud Relationship State Local-341',
						'zGenAlbum-Cloud Owner Mail Key-342',
						'zGenAlbum-Cloud Owner Frist Name-343',
						'zGenAlbum-Cloud Owner Last Name-344',
						'zGenAlbum-Cloud Owner Full Name-345',
						'zGenAlbum-Cloud Person ID-346',
						'zAsset-Cloud Owner Hashed Person ID-347',
						'zGenAlbum-Cloud Owner Hashed Person ID-348',
						'zGenAlbum-Local Cloud Multi-Contributors Enabled-349',
						'zGenAlbum-Cloud Multi-Contributors Enabled-350',
						'zGenAlbum-Cloud Album Sub Type-351',
						('zGenAlbum-Cloud Contribution Date-352', 'datetime'),
						('zGenAlbum-Cloud Last Interesting Change Date-353', 'datetime'),
						'zGenAlbum-Cloud Notification Enabled-354',
						'ParentzGenAlbum-Pinned-355',
						'zGenAlbum-Pinned-356',
						'ParentzGenAlbum-Custom Sort Key-357',
						'zGenAlbum-Custom Sort Key-358',
						'ParentzGenAlbum-Custom Sort Ascending-359',
						'zGenAlbum-Custom Sort Ascending-360',
						'ParentzGenAlbum-Is Prototype-361',
						'zGenAlbum-Is Prototype-362',
						'ParentzGenAlbum-Project Document Type-363',
						'zGenAlbum-Project Document Type-364',
						'ParentzGenAlbum-Custom Query Type-365',
						'zGenAlbum-Custom Query Type-366',
						'ParentzGenAlbum-Trashed State-367',
						('ParentzGenAlbum-Trash Date-368', 'datetime'),
						'zGenAlbum-Trashed State-369',
						('zGenAlbum-Trash Date-370', 'datetime'),
						'ParentzGenAlbum-Cloud Delete State-371',
						'zGenAlbum-Cloud Delete State-372',
						'zGenAlbum-Cloud Owner Whitelisted-373',
						'zGenAlbum-Cloud Local Public URL Enabled-374',
						'zGenAlbum-Cloud Public URL Enabled-375',
						'zGenAlbum-Public URL-376',
						'zGenAlbum-Key Asset Face Thumb Index-377',
						'zGenAlbum-Project Text Extension ID-378',
						'zGenAlbum-User Query Data-379',
						'zGenAlbum-Custom Query Parameters-380',
						'zGenAlbum-Project Data-381',
						'zCldShareAlbumInvRec-Is My Invitation to Shared Album-382',
						'zCldShareAlbumInvRec-Invitation State Local-383',
						'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-384',
						('zCldShareAlbumInvRec-Subscription Date-385', 'datetime'),
						'zCldShareAlbumInvRec-Invitee First Name-386',
						'zCldShareAlbumInvRec-Invitee Last Name-387',
						'zCldShareAlbumInvRec-Invitee Full Name-388',
						'zCldShareAlbumInvRec-Invitee Hashed Person ID-389',
						'zCldShareAlbumInvRec-Invitee Email Key-390',
						'zGenAlbum-Key Asset Face ID-391',
						'zFaceCrop-Face Area Points-392',
						'zAsset-Face Adjustment Version-393',
						'zDetFace-Asset Visible-394',
						'zPerson-Face Count-395',
						'zDetFace-Face Crop-396',
						'zDetFace-Face Algorithm Version-397',
						'zDetFace-Adjustment Version-398',
						'zDetFace-UUID-4TableStart-399',
						'zPerson-Person UUID-4TableStart-400',
						'zDetFace-Confirmed Face Crop Generation State-401',
						'zDetFace-Manual-402',
						'zDetFace-VIP Model Type-403',
						'zDetFace-Name Source-404',
						'zDetFace-Cloud Name Source-405',
						'zPerson-Person URI-406',
						'zPerson-Display Name-407',
						'zPerson-Full Name-408',
						'zPerson-Cloud Verified Type-409',
						'zFaceCrop-State-410',
						'zFaceCrop-Type-411',
						'zFaceCrop-UUID-4TableStart-412',
						'zPerson-Type-413',
						'zPerson-Verified Type-414',
						'zPerson-Gender Type-415',
						'zDetFace-Gender Type-416',
						'zDetFace-Center X-417',
						'zDetFace-Center Y-418',
						'zPerson-Age Type Estimate-419',
						'zDetFace-Age Type Estimate-420',
						'zDetFace-Hair Color Type-421',
						'zDetFace-Facial Hair Type-422',
						'zDetFace-Has Smile-423',
						'zDetFace-Smile Type-424',
						'zDetFace-Lip Makeup Type-425',
						'zDetFace-Eyes State-426',
						'zDetFace-Is Left Eye Closed-427',
						'zDetFace-Is Right Eye Closed-428',
						'zDetFace-Eye Glasses Type-429',
						'zDetFace-Eye Makeup Type-430',
						'zDetFace-Cluster Squence Number Key-431',
						'zDetFace-Grouping ID-432',
						'zDetFace-Master ID-433',
						'zDetFace-Quality-434',
						'zDetFace-Quality Measure-435',
						'zDetFace-Source Height-436',
						'zDetFace-Source Width-437',
						'zDetFace-Hidden-Asset Hidden-438',
						'zDetFace-In Trash-Recently Deleted-439',
						'zDetFace-Cloud Local State-440',
						'zDetFace-Training Type-441',
						'zDetFace.Pose Yaw-442',
						'zDetFace-Roll-443',
						'zDetFace-Size-444',
						'zDetFace-Cluster Squence Number-445',
						'zDetFace-Blur Score-446',
						'zDetFacePrint-Face Print Version-447',
						'zMedAnlyAstAttr-Face Count-448',
						'zDetFaceGroup-UUID-4TableStart-449',
						'zDetFaceGroup-Person Builder State-450',
						'zDetFaceGroup-UnNamed Face Count-451',
						'zPerson-In Person Naming Model-452',
						'zPerson-Key Face Pick Source Key-453',
						'zPerson-Manual Order Key-454',
						'zPerson-Question Type-455',
						'zPerson-Suggested For Client Type-456',
						'zPerson-Merge Target Person-457',
						'zPerson-Cloud Local State-458',
						'zFaceCrop-Cloud Local State-459',
						'zFaceCrop-Cloud Type-460',
						'zPerson-Cloud Delete State-461',
						'zFaceCrop-Cloud Delete State-462',
						'zFaceCrop-Invalid Merge Canidate Person UUID-4TableStart-463',
						'zMemory-zPK-464',
						'z3MemoryBCAs-3CuratedAssets = zAsset-zPK-465',
						'z3MemoryBCAs-40MemoriesBeingCuratedAssets = zMemory-zPK-466',
						'z3MemoryBECAs-3ExtCuratedAssets = zAsset-zPK-467',
						'z3MemoryBECAs-40MemoriesBeingExtCuratedAssets = zMemory-zPK-468',
						'z3MemoryBMCAs-3MovieCuratedAssets = zAsset-zPK-469',
						'z3MemoryBMCAs-40MemoriesBeingMovieCuratedAssets = zMemory-zPK-470',
						'z3MemoryBRAs-3RepresentativeAssets = zAsset-zPK-471',
						'z3MemoryBRAs-40RepresentativeAssets = zMemory-zPK-472',
						'zMemory-Key Asset = zAsset-zPK-473',
						'zMemory-UUID-474',
						'zMemory-SubTitle-475',
						'zMemory-Title-476',
						'zMemory-Category-477',
						'zMemory-SubCategory-478',
						('zMemory-Creation Date-479', 'datetime'),
						'zMemory-User Created-480',
						'zMemory-Favorite Memory-481',
						'zMemory-Score-482',
						'zMemory-View Count-483',
						'zMemory-Play Count-484',
						'zMemory-Rejected-485',
						'zMemory-Share Count-486',
						('zMemory-Last Movie Play Date-487', 'datetime'),
						('zMemory-Last Viewed Date-488', 'datetime'),
						'zMemory-Pending-489',
						'zMemory-Pending Play Count Memory-490',
						'zMemory-Pending Share Count Memory-491',
						'zMemory-Pending View Count Memory-492',
						'zMemory-Featured State-493',
						'zMemory-Photos Graph Version-494',
						'zMemory-AssetListPredicte-495',
						'zMemory-Notification State-496',
						'zMemory-Cloud Local State-497',
						'zMemory-Cloud Delete State-498',
						'YearzMomentList-UUID-499',
						'YearzMomentList-zPK-500',
						'zMoment-Year Moment List-501',
						'YearzMomentList-Sort Index-502',
						'YearzMomentList-Granularity Level-503',
						('YearzMomentList-Start Date-504', 'datetime'),
						('YearzMomentList-Representative Date-505', 'datetime'),
						('YearzMomentList-End Date-506', 'datetime'),
						'YearzMomentList-Trashed State-507',
						'MegaYMzMomentList-UUID-508',
						'MegaYMzMomentList-zPK-509',
						'zMoment-Mega Moment List-510',
						'MegaYMzMomentList-Sort Index-511',
						'MegaYMzMomentList-Granularity Level-512',
						('MegaYMzMomentList-Start Date-513', 'datetime'),
						('MegaYMzMomentList-Representative Date-514', 'datetime'),
						('MegaYMzMomentList-End Date-515', 'datetime'),
						'MegaYMzMomentList-Trashed State-516',
						'zMoment-UUID-517',
						'zMoment-zPK-518',
						'zMoment-Aggregation Score-519',
						('zMoment-Start Date-520', 'datetime'),
						('zMoment-Representative Date-521', 'datetime'),
						'zMoment-Timezone Offset-522',
						('zMoment-Modification Date-523', 'datetime'),
						('zMoment-End Date-524', 'datetime'),
						'zMoment-SubTitle-525',
						'zMoment-Title-526',
						'zMoment-Processed Location-527',
						'zMoment-Approx Latitude-528',
						'zMoment-Approx Longitude-529',
						'zMoment-GPS Horizontal Accuracy-530',
						'zMoment-Cache Count-531',
						'zMoment-Cached Photos Count-532',
						'zMoment-Cached Videos Count-533',
						'zMoment-Trashed State-534',
						'zMoment-Highlight Key-535',
						'zAsset-Highlight Visibility Score-536',
						'YearParzPhotosHigh-UUID-537',
						'YearParzPhotosHigh-zPK-538',
						'YearParzPhotosHigh-zENT-539',
						'YearParzPhotosHigh-zOPT-540',
						'YearParzPhotosHigh-Promotion Score-541',
						'YearParzPhotosHigh-Title-542',
						'YearParzPhotosHigh-Verbose Smart Description-543',
						('YearParzPhotosHigh-Start Date-544', 'datetime'),
						('YearParzPhotosHigh-End Date-545', 'datetime'),
						'YearParzPhotosHigh-Year Key Asset-546',
						'YearParzPhotosHigh-Is Curated-547',
						'YearParzPhotosHigh-Kind-548',
						'YearParzPhotosHigh-Category-549',
						'YearParzPhotosHigh-Visibility State-550',
						'YearParzPhotosHigh-Enrichment State-551',
						'YearParzPhotosHigh-Enrichment Version-552',
						'YearParzPhotosHigh-Highlight Version-553',
						'YMParzPhotosHigh-UUID-554',
						'YMParzPhotosHigh-zPK-555',
						'YMParzPhotosHigh-Parent PH Key-556',
						'YMParzPhotosHigh-zENT-557',
						'YMParzPhotosHigh-zOPT-558',
						'YMParzPhotosHigh-Promotion Score-559',
						'YMParzPhotosHigh-Title-560',
						'YMParzPhotosHigh-Subtitle-561',
						'YMParzPhotosHigh-Verbose Smart Description-562',
						('YMParzPhotosHigh-Start Date-563', 'datetime'),
						('YMParzPhotosHigh-End Date-564', 'datetime'),
						'YMParzPhotosHigh-Month First Asset-565',
						'YMParzPhotosHigh-Month Key Asset-566',
						'YMParzPhotosHigh-Is Curated-567',
						'YMParzPhotosHigh-Kind-568',
						'YMParzPhotosHigh-Category-569',
						'YMParzPhotosHigh-Visibility State-570',
						'YMParzPhotosHigh-Enrichment State-571',
						'YMParzPhotosHigh-Enrichment Version-572',
						'YMParzPhotosHigh-Highlight Version-573',
						'DGParzPhotosHigh-UUID-574',
						'DGParzPhotosHigh-zPK-575',
						'DGParzPhotosHigh-Parent PH Key-576',
						'DGParzPhotosHigh-zENT-577',
						'DGParzPhotosHigh-zOPT-578',
						'DGParzPhotosHigh-Promotion Score-579',
						'DGParzPhotosHigh-Title-580',
						'DGParzPhotosHigh-Subtitle-581',
						'DGParzPhotosHigh-Verbose Smart Description-582',
						('DGParzPhotosHigh-Start Date-583', 'datetime'),
						('DGParzPhotosHigh-End Date-584', 'datetime'),
						'DGParzPhotosHigh-Month First Asset-585',
						'DGParzPhotosHigh-Month Key Asset-586',
						'DGParzPhotosHigh-Is Curated-587',
						'DGParzPhotosHigh-Kind-588',
						'DGParzPhotosHigh-Category-589',
						'DGParzPhotosHigh-Visibility State-590',
						'DGParzPhotosHigh-Enrichment State-591',
						'DGParzPhotosHigh-Enrichment Version-592',
						'DGParzPhotosHigh-Highlight Version-593',
						'zAsset-Highlight Being Assets Key-594',
						'HBAzPhotosHigh-UUID-595',
						'HBAzPhotosHigh-zPK-596',
						'HBAzPhotosHigh-Parent PH Key-597',
						'HBAzPhotosHigh-zENT-598',
						'HBAzPhotosHigh-zOPT-599',
						'HBAzPhotosHigh-Promotion Score-600',
						'HBAzPhotosHigh-Title-601',
						'HBAzPhotosHigh-Subtitle-602',
						'HBAzPhotosHigh-Verbose Smart Description-603',
						('HBAzPhotosHigh-Start Date-604', 'datetime'),
						'HBAzPhotosHigh Start-Timezone Offset-605',
						'HBAzPhotosHigh-End Timezone Offset-606',
						('HBAzPhotosHigh-End Date-607', 'datetime'),
						'HBAzPhotosHigh-Asset Count-608',
						'HBAzPhotosHigh-Summary Count-609',
						'HBAzPhotosHigh-Extended Count-610',
						'HBAzPhotosHigh-Day Group Assets Count-611',
						'HBAzPhotosHigh-Day Group Ext Assets Count-612',
						'HBAzPhotosHigh-Day Group Summary Assets Count-613',
						'HBAzPhotosHigh-Key Asset-614',
						'HBAzPhotosHigh-Is Curated-615',
						'HBAzPhotosHigh-Type-616',
						'HBAzPhotosHigh-Kind-617',
						'HBAzPhotosHigh-Category-618',
						'HBAzPhotosHigh-Visibility State-619',
						'HBAzPhotosHigh-Mood-620',
						'HBAzPhotosHigh-Enrichment State-621',
						'HBAzPhotosHigh-Enrichment Version-622',
						'HBAzPhotosHigh-Highlight Version-623',
						'zAsset-Highlight Being Extended Assets Key-624',
						'HBEAzPhotosHigh-UUID-625',
						'HBEAzPhotosHigh-zPK-626',
						'HBEAzPhotosHigh-zENT-627',
						'HBEAzPhotosHigh-zOPT-628',
						'HBEAzPhotosHigh-Promotion Score-629',
						'HBEAzPhotosHigh-Title-630',
						'HBEAzPhotosHigh-Subtitle-631',
						'HBEAzPhotosHigh-Verbose Smart Description-632',
						('HBEAzPhotosHigh-Start Date-633', 'datetime'),
						'HBEAzPhotosHigh-Start Timezone Offset-634',
						'HBEAzPhotosHigh-End Timezone Offset-635',
						('HBEAzPhotosHigh-End Date-636', 'datetime'),
						'HBEAzPhotosHigh-Asset Count-637',
						'HBEAzPhotosHigh-Summary Count-638',
						'HBEAzPhotosHigh-Extended Count-639',
						'HBEAzPhotosHigh-Day Group Assets Count-640',
						'HBEAzPhotosHigh-Day Group Ext Assets Count-641',
						'HBEAzPhotosHigh-Day Group Summary Assets Count-642',
						'HBEAzPhotosHigh-Parent PH Key-643',
						'HBEAzPhotosHigh-Year Key Asset-644',
						'HBEAzPhotosHigh-Month First Asset-645',
						'HBEAzPhotosHigh-Month Key Asset-646',
						'HBEAzPhotosHigh-Key Asset-647',
						'HBEAzPhotosHigh-Parent Day Group PH Key-648',
						'HBEAzPhotosHigh-Day Group Key Asset-649',
						'HBEAzPhotosHigh-is Curated-650',
						'HBEAzPhotosHigh-Type-651',
						'HBEAzPhotosHigh-Kind-652',
						'HBEAzPhotosHigh-Category-653',
						'HBEAzPhotosHigh-Visibility State-654',
						'HBEAzPhotosHigh-Mood-655',
						'HBEAzPhotosHigh-Enrichment State-656',
						'HBEAzPhotosHigh-Enrichment Version-657',
						'HBEAzPhotosHigh-Highlight Version-658',
						'zAsset-Highlight Being Summary Assets Key-659',
						'HBSAzPhotosHigh-UUID-660',
						'HBSAzPhotosHigh-zPK-661',
						'HBSAzPhotosHigh-zENT-662',
						'HBSAzPhotosHigh-zOPT-663',
						'HBSAzPhotosHigh-Promotion Score-664',
						'HBSAzPhotosHigh-Title-665',
						'HBSAzPhotosHigh-Subtitle-666',
						'HBSAzPhotosHigh-Verbose Smart Description-667',
						('HBSAzPhotosHigh-Start Date-668', 'datetime'),
						'HBSAzPhotosHigh-Start Timezone Offset-669',
						'HBSAzPhotosHigh-End Timezone Offset-670',
						('HBSAzPhotosHigh-End Date-671', 'datetime'),
						'HBSAzPhotosHigh-Asset Count-672',
						'HBSAzPhotosHigh-Summary Count-673',
						'HBSAzPhotosHigh-Extended Count-674',
						'HBSAzPhotosHigh-Day Group Assets Count-675',
						'HBSAzPhotosHigh-Day Group Ext Assets Count-676',
						'HBSAzPhotosHigh-Day Group Summary Assets Count-677',
						'HBSAzPhotosHigh-Parent PH Key-678',
						'HBSAzPhotosHigh-Year Key Asset-679',
						'HBSAzPhotosHigh-Month First Asset-680',
						'HBSAzPhotosHigh-Month Key Asset-681',
						'HBSAzPhotosHigh-Key Asset-682',
						'HBSAzPhotosHigh-Parent Day Group PH Key-683',
						'HBSAzPhotosHigh-Day Group Key Asset-684',
						'HBSAzPhotosHigh-is Curated-685',
						'HBSAzPhotosHigh-Type-686',
						'HBSAzPhotosHigh-Kind-687',
						'HBSAzPhotosHigh-Category-688',
						'HBSAzPhotosHigh-Visibility State-689',
						'HBSAzPhotosHigh-Mood-690',
						'HBSAzPhotosHigh-Enrichment State-691',
						'HBSAzPhotosHigh-Enrichment Version-692',
						'HBSAzPhotosHigh-Highlight Version-693',
						'zAsset-Highlight Being Key Asset Key-694',
						'HBKAzPhotosHigh-UUID-695',
						'HBKAzPhotosHigh-zPK-696',
						'HBKAzPhotosHigh-zENT-697',
						'HBKAzPhotosHigh-zOPT-698',
						'HBKAzPhotosHigh-Promotion Score-699',
						'HBKAzPhotosHigh-Title-700',
						'HBKAzPhotosHigh-Subtitle-701',
						'HBKAzPhotosHigh-Verbose Smart Description-702',
						('HBKAzPhotosHigh-Start Date-703', 'datetime'),
						'HBKAzPhotosHigh-Start Timezone Offset-704',
						'HBKAzPhotosHigh-End Timezone Offset-705',
						('HBKAzPhotosHigh-End Date-706', 'datetime'),
						'HBKAzPhotosHigh-Asset Count-707',
						'HBKAzPhotosHigh-Summary Count-708',
						'HBKAzPhotosHigh-Extended Count-709',
						'HBKAzPhotosHigh-Day Group Assets Count-710',
						'HBKAzPhotosHigh-Day Group Ext Assets Count-711',
						'HBKAzPhotosHigh-Day Group Summary Assets Count-712',
						'HBKAzPhotosHigh-Parent PH Key-713',
						'HBKAzPhotosHigh-Year Key Asset-714',
						'HBKAzPhotosHigh-Month First Asset-715',
						'HBKAzPhotosHigh-Month Key Asset-716',
						'HBKAzPhotosHigh-Key Asset-717',
						'HBKAzPhotosHigh-Parent Day Group PH Key-718',
						'HBKAzPhotosHigh-Day Group Key Asset-719',
						'HBKAzPhotosHigh-is Curated-720',
						'HBKAzPhotosHigh-Type-721',
						'HBKAzPhotosHigh-Kind-722',
						'HBKAzPhotosHigh-Category-723',
						'HBKAzPhotosHigh-Visibility State-724',
						'HBKAzPhotosHigh-Mood-725',
						'HBKAzPhotosHigh-Enrichment State-726',
						'HBKAzPhotosHigh-Enrichment Version-727',
						'HBKAzPhotosHigh-Highlight Version-728',
						'zAsset-Day Group Highlight Being Assets Key-729',
						'DGHBAzPhotosHigh-UUID-730',
						'DGHBAzPhotosHigh-zPK-731',
						'DGHBAzPhotosHigh-zENT-732',
						'DGHBAzPhotosHigh-zOPT-733',
						'DGHBAzPhotosHigh-Promotion Score-734',
						'DGHBAzPhotosHigh-Title-735',
						'DGHBAzPhotosHigh-Subtitle-736',
						'DGHBAzPhotosHigh-Verbose Smart Description-737',
						('DGHBAzPhotosHigh-Start Date-738', 'datetime'),
						'DGHBAzPhotosHigh-Start Timezone Offset-739',
						'DGHBAzPhotosHigh-End Timezone Offset-740',
						('DGHBAzPhotosHigh-End Date-741', 'datetime'),
						'DGHBAzPhotosHigh-Asset Count-742',
						'DGHBAzPhotosHigh-Summary Count-743',
						'DGHBAzPhotosHigh-Extended Count-744',
						'DGHBAzPhotosHigh-Day Group Assets Count-745',
						'DGHBAzPhotosHigh-Day Group Ext Assets Count-746',
						'DGHBAzPhotosHigh-Day Group Summary Assets Count-747',
						'DGHBAzPhotosHigh-Parent PH Key-748',
						'DGHBAzPhotosHigh-Year Key Asset-749',
						'DGHBAzPhotosHigh-Month First Asset-750',
						'DGHBAzPhotosHigh-Month Key Asset-751',
						'DGHBAzPhotosHigh-Key Asset-752',
						'DGHBAzPhotosHigh-Parent Day Group PH Key-753',
						'DGHBAzPhotosHigh-Day Group Key Asset-754',
						'DGHBAzPhotosHigh-is Curated-755',
						'DGHBAzPhotosHigh-Type-756',
						'DGHBAzPhotosHigh-Kind-757',
						'DGHBAzPhotosHigh-Category-758',
						'DGHBAzPhotosHigh-Visibility State-759',
						'DGHBAzPhotosHigh-Mood-760',
						'DGHBAzPhotosHigh-Enrichment State-761',
						'DGHBAzPhotosHigh-Enrichment Version-762',
						'DGHBAzPhotosHigh-Highlight Version-763',
						'zAsset-Day Group Highlight Being Extended Assets Key-764',
						'DGHBEAzPhotosHigh-UUID-765',
						'DGHBEAzPhotosHigh-zPK-766',
						'DGHBEAzPhotosHigh-zENT-767',
						'DGHBEAzPhotosHigh-zOPT-768',
						'DGHBEAzPhotosHigh-Promotion Score-769',
						'DGHBEAzPhotosHigh-Title-770',
						'DGHBEAzPhotosHigh-Subtitle-771',
						'DGHBEAzPhotosHigh-Verbose Smart Description-772',
						('DGHBEAzPhotosHigh-Start Date-773', 'datetime'),
						'DGHBEAzPhotosHigh-Start Timezone Offset-774',
						'DGHBEAzPhotosHigh-End Timezone Offset-775',
						('DGHBEAzPhotosHigh-End Date-776', 'datetime'),
						'DGHBEAzPhotosHigh-Asset Count-777',
						'DGHBEAzPhotosHigh-Summary Count-778',
						'DGHBEAzPhotosHigh-Extended Count-779',
						'DGHBEAzPhotosHigh-Day Group Assets Count-780',
						'DGHBEAzPhotosHigh-Day Group Ext Assets Count-781',
						'DGHBEAzPhotosHigh-Day Group Summary Assets Count-782',
						'DGHBEAzPhotosHigh-Parent PH Key-783',
						'DGHBEAzPhotosHigh-Year Key Asset-784',
						'DGHBEAzPhotosHigh-Month First Asset-785',
						'DGHBEAzPhotosHigh-Month Key Asset-786',
						'DGHBEAzPhotosHigh-Key Asset-787',
						'DGHBEAzPhotosHigh-Parent Day Group PH Key-788',
						'DGHBEAzPhotosHigh-Day Group Key Asset-789',
						'DGHBEAzPhotosHigh-is Curated-790',
						'DGHBEAzPhotosHigh-Type-791',
						'DGHBEAzPhotosHigh-Kind-792',
						'DGHBEAzPhotosHigh-Category-793',
						'DGHBEAzPhotosHigh-Visibility State-794',
						'DGHBEAzPhotosHigh-Mood-795',
						'DGHBEAzPhotosHigh-Enrichment State-796',
						'DGHBEAzPhotosHigh-Enrichment Version-797',
						'DGHBEAzPhotosHigh-Highlight Version-798',
						'zAsset-Day Group Highlight Being Key Asset-799',
						'DGHBKAzPhotosHigh-UUID-800',
						'DGHBKAzPhotosHigh-zPK-801',
						'DGHBKAzPhotosHigh-zENT-802',
						'DGHBKAzPhotosHigh-zOPT-803',
						'DGHBKAzPhotosHigh-Promotion Score-804',
						'DGHBKAzPhotosHigh-Title-805',
						'DGHBKAzPhotosHigh-Subtitle-806',
						'DGHBKAzPhotosHigh-Verbose Smart Description-807',
						('DGHBKAzPhotosHigh-Start Date-808', 'datetime'),
						'DGHBKAzPhotosHigh-Start Timezone Offset-809',
						'DGHBKAzPhotosHigh-End Timezone Offset-810',
						('DGHBKAzPhotosHigh-End Date-811', 'datetime'),
						'DGHBKAzPhotosHigh-Asset Count-812',
						'DGHBKAzPhotosHigh-Summary Count-813',
						'DGHBKAzPhotosHigh-Extended Count-814',
						'DGHBKAzPhotosHigh-Day Group Assets Count-815',
						'DGHBKAzPhotosHigh-Day Group Ext Assets Count-816',
						'DGHBKAzPhotosHigh-Day Group Summary Assets Count-817',
						'DGHBKAzPhotosHigh-Parent PH Key-818',
						'DGHBKAzPhotosHigh-Year Key Asset-819',
						'DGHBKAzPhotosHigh-Month First Asset-820',
						'DGHBKAzPhotosHigh-Month Key Asset-821',
						'DGHBKAzPhotosHigh-Key Asset-822',
						'DGHBKAzPhotosHigh-Parent Day Group PH Key-823',
						'DGHBKAzPhotosHigh-Day Group Key Asset-824',
						'DGHBKAzPhotosHigh-is Curated-825',
						'DGHBKAzPhotosHigh-Type-826',
						'DGHBKAzPhotosHigh-Kind-827',
						'DGHBKAzPhotosHigh-Category-828',
						'DGHBKAzPhotosHigh-Visibility State-829',
						'DGHBKAzPhotosHigh-Mood-830',
						'DGHBKAzPhotosHigh-Enrichment State-831',
						'DGHBKAzPhotosHigh-Enrichment Version-832',
						'DGHBKAzPhotosHigh-Highlight Version-833',
						'zAsset-Day Group Highlight Being Summary Assets Key-834',
						'DGHBSAzPhotosHigh-UUID-835',
						'DGHBSAzPhotosHigh-zPK-836',
						'DGHBSAzPhotosHigh-zENT-837',
						'DGHBSAzPhotosHigh-zOPT-838',
						'DGHBSAzPhotosHigh-Promotion Score-839',
						'DGHBSAzPhotosHigh-Title-840',
						'DGHBSAzPhotosHigh-Subtitle-841',
						'DGHBSAzPhotosHigh-Verbose Smart Description-842',
						('DGHBSAzPhotosHigh-Start Date-843', 'datetime'),
						'DGHBSAzPhotosHigh-Start Timezone Offset-844',
						'DGHBSAzPhotosHigh-End Timezone Offset-845',
						('DGHBSAzPhotosHigh-End Date-846', 'datetime'),
						'DGHBSAzPhotosHigh-Asset Count-847',
						'DGHBSAzPhotosHigh-Summary Count-848',
						'DGHBSAzPhotosHigh-Extended Count-849',
						'DGHBSAzPhotosHigh-Day Group Assets Count-850',
						'DGHBSAzPhotosHigh-Day Group Ext Assets Count-851',
						'DGHBSAzPhotosHigh-Day Group Summary Assets Count-852',
						'DGHBSAzPhotosHigh-Parent PH Key-853',
						'DGHBSAzPhotosHigh-Year Key Asset-854',
						'DGHBSAzPhotosHigh-Month First Asset-855',
						'DGHBSAzPhotosHigh-Month Key Asset-856',
						'DGHBSAzPhotosHigh-Key Asset-857',
						'DGHBSAzPhotosHigh-Parent Day Group PH Key-858',
						'DGHBSAzPhotosHigh-Day Group Key Asset-859',
						'DGHBSAzPhotosHigh-is Curated-860',
						'DGHBSAzPhotosHigh-Type-861',
						'DGHBSAzPhotosHigh-Kind-862',
						'DGHBSAzPhotosHigh-Category-863',
						'DGHBSAzPhotosHigh-Visibility State-864',
						'DGHBSAzPhotosHigh-Mood-865',
						'DGHBSAzPhotosHigh-Enrichment State-866',
						'DGHBSAzPhotosHigh-Enrichment Version-867',
						'DGHBSAzPhotosHigh-Highlight Version-868',
						'zAsset-Month Highlight Being First Asset Key-869',
						'MHBFAzPhotosHigh-UUID-870',
						'MHBFAzPhotosHigh-zPK-871',
						'MHBFAzPhotosHigh-zENT-872',
						'MHBFAzPhotosHigh-zOPT-873',
						'MHBFAzPhotosHigh-Promotion Score-874',
						'MHBFAzPhotosHigh-Title-875',
						'MHBFAzPhotosHigh-Subtitle-876',
						'MHBFAzPhotosHigh-Verbose Smart Description-877',
						('MHBFAzPhotosHigh-Start Date-878', 'datetime'),
						'MHBFAzPhotosHigh-Start Timezone Offset-879',
						'MHBFAzPhotosHigh-End Timezone Offset-880',
						('MHBFAzPhotosHigh-End Date-881', 'datetime'),
						'MHBFAzPhotosHigh-Asset Count-882',
						'MHBFAzPhotosHigh-Summary Count-883',
						'MHBFAzPhotosHigh-Extended Count-884',
						'MHBFAzPhotosHigh-Day Group Assets Count-885',
						'MHBFAzPhotosHigh-Day Group Ext Assets Count-886',
						'MHBFAzPhotosHigh-Day Group Summary Assets Count-887',
						'MHBFAzPhotosHigh-Parent PH Key-888',
						'MHBFAzPhotosHigh-Year Key Asset-889',
						'MHBFAzPhotosHigh-Month First Asset-890',
						'MHBFAzPhotosHigh-Month Key Asset-891',
						'MHBFAzPhotosHigh-Key Asset-892',
						'MHBFAzPhotosHigh-Parent Day Group PH Key-893',
						'MHBFAzPhotosHigh-Day Group Key Asset-894',
						'MHBFAzPhotosHigh-is Curated-895',
						'MHBFAzPhotosHigh-Type-896',
						'MHBFAzPhotosHigh-Kind-897',
						'MHBFAzPhotosHigh-Category-898',
						'MHBFAzPhotosHigh-Visibility State-899',
						'MHBFAzPhotosHigh-Mood-900',
						'MHBFAzPhotosHigh-Enrichment State-901',
						'MHBFAzPhotosHigh-Enrichment Version-902',
						'MHBFAzPhotosHigh-Highlight Version-903',
						'zAsset-Month Highlight Being Key Asset-904',
						'MHBKAzPhotosHigh-UUID-905',
						'MHBKAzPhotosHigh-zPK-906',
						'MHBKAzPhotosHigh-zENT-907',
						'MHBKAzPhotosHigh-zOPT-908',
						'MHBKAzPhotosHigh-Promotion Score-909',
						'MHBKAzPhotosHigh-Title-910',
						'MHBKAzPhotosHigh-Subtitle-911',
						'MHBKAzPhotosHigh-Verbose Smart Description-912',
						('MHBKAzPhotosHigh-Start Date-913', 'datetime'),
						'MHBKAzPhotosHigh-Start Timezone Offset-914',
						'MHBKAzPhotosHigh-End Timezone Offset-915',
						('MHBKAzPhotosHigh-End Date-916', 'datetime'),
						'MHBKAzPhotosHigh-Asset Count-917',
						'MHBKAzPhotosHigh-Summary Count-918',
						'MHBKAzPhotosHigh-Extended Count-919',
						'MHBKAzPhotosHigh-Day Group Assets Count-920',
						'MHBKAzPhotosHigh-Day Group Ext Assets Count-921',
						'MHBKAzPhotosHigh-Day Group Summary Assets Count-922',
						'MHBKAzPhotosHigh-Parent PH Key-923',
						'MHBKAzPhotosHigh-Year Key Asset-924',
						'MHBKAzPhotosHigh-Month First Asset-925',
						'MHBKAzPhotosHigh-Month Key Asset-926',
						'MHBKAzPhotosHigh-Key Asset-927',
						'MHBKAzPhotosHigh-Parent Day Group PH Key-928',
						'MHBKAzPhotosHigh-Day Group Key Asset-929',
						'MHBKAzPhotosHigh-is Curated-930',
						'MHBKAzPhotosHigh-Type-931',
						'MHBKAzPhotosHigh-Kind-932',
						'MHBKAzPhotosHigh-Category-933',
						'MHBKAzPhotosHigh-Visibility State-934',
						'MHBKAzPhotosHigh-Mood-935',
						'MHBKAzPhotosHigh-Enrichment State-936',
						'MHBKAzPhotosHigh-Enrichment Version-937',
						'MHBKAzPhotosHigh-Highlight Version-938',
						'zAsset-Year Highlight Being Key Asset-939',
						'YHBKAzPhotosHigh-UUID-940',
						'YHBKAzPhotosHigh-zPK-941',
						'YHBKAzPhotosHigh-zENT-942',
						'YHBKAzPhotosHigh-zOPT-943',
						'YHBKAzPhotosHigh-Promotion Score-944',
						'YHBKAzPhotosHigh-Title-945',
						'YHBKAzPhotosHigh-Subtitle-946',
						'YHBKAzPhotosHigh-Verbose Smart Description-947',
						('YHBKAzPhotosHigh-Start Date-948', 'datetime'),
						'YHBKAzPhotosHigh-Start Timezone Offset-949',
						'YHBKAzPhotosHigh-End Timezone Offset-950',
						('YHBKAzPhotosHigh-End Date-951', 'datetime'),
						'YHBKAzPhotosHigh-Asset Count-952',
						'YHBKAzPhotosHigh-Summary Count-953',
						'YHBKAzPhotosHigh-Extended Count-954',
						'YHBKAzPhotosHigh-Day Group Assets Count-955',
						'YHBKAzPhotosHigh-Day Group Ext Assets Count-956',
						'YHBKAzPhotosHigh-Day Group Summary Assets Count-957',
						'YHBKAzPhotosHigh-Parent PH Key-958',
						'YHBKAzPhotosHigh-Year Key Asset-959',
						'YHBKAzPhotosHigh-Month First Asset-960',
						'YHBKAzPhotosHigh-Month Key Asset-961',
						'YHBKAzPhotosHigh-Key Asset-962',
						'YHBKAzPhotosHigh-Parent Day Group PH Key-963',
						'YHBKAzPhotosHigh-Day Group Key Asset-964',
						'YHBKAzPhotosHigh-is Curated-965',
						'YHBKAzPhotosHigh-Type-966',
						'YHBKAzPhotosHigh-Kind-967',
						'YHBKAzPhotosHigh-Category-968',
						'YHBKAzPhotosHigh-Visibility State-969',
						'YHBKAzPhotosHigh-Mood-970',
						'YHBKAzPhotosHigh-Enrichment State-971',
						'YHBKAzPhotosHigh-Enrichment Version-972',
						'YHBKAzPhotosHigh-Highlight Version-973',
						'z3SuggBKA-3KeyAssets = zAsset-zPK-974',
						'z3SuggBKA-55SuggBeingKeyAssets = zSugg-zPK-975',
						'SBKAzSugg-zPK-976',
						'SBKAzSugg-UUID-977',
						('SBKAzSugg-Start Date-978', 'datetime'),
						'SBKAzSugg-State-979',
						'SBKAzSugg-Featured State-980',
						'SBKAzSugg-Notification State-981',
						('SBKAzSugg-Creation Date-982', 'datetime'),
						('SBKAzSugg-End Date-983', 'datetime'),
						('SBKAzSugg-Activation Date-984', 'datetime'),
						('SBKAzSugg-Expunge Date-985', 'datetime'),
						('SBKAzSugg-Relevant Until Date-986', 'datetime'),
						'SBKAzSugg-Title-987',
						'SBKAzSugg-Sub Title-988',
						'SBKAzSugg-Cached Count-989',
						'SBKAzSugg-Cahed Photos Count-990',
						'SBKAzSugg-Cached Videos Count-991',
						'SBKAzSugg-Type-992',
						'SBKAzSugg-Sub Type-993',
						'SBKAzSugg-Version-994',
						'SBKAzSugg-Cloud Local State-995',
						'SBKAzSugg-Cloud Delete State-996',
						'z3SuggBRA-3RepAssets1-997',
						'z3SuggBRA-55SuggBeingRepAssets-998',
						'SBRAzSugg-zPK-999',
						'SBRAzSugg-UUID-1000',
						('SBRAzSugg-Start Date-1001', 'datetime'),
						'SBRAzSugg-State-1002',
						'SBRAzSugg-Featured State-1003',
						'SBRAzSugg-Notification State-1004',
						('SBRAzSugg-Creation Date-1005', 'datetime'),
						('SBRAzSugg-End Date-1006', 'datetime'),
						('SBRAzSugg-Activation Date-1007', 'datetime'),
						('SBRAzSugg-Expunge Date-1008', 'datetime'),
						('SBRAzSugg-Relevant Until Date-1009', 'datetime'),
						'SBRAzSugg-Title-1010',
						'SBRAzSugg-Sub Title-1011',
						'SBRAzSugg-Cached Count-1012',
						'SBRAzSugg-Cahed Photos Count-1013',
						'SBRAzSugg-Cached Videos Count-1014',
						'SBRAzSugg-Type-1015',
						'SBRAzSugg-Sub Type-1016',
						'SBRAzSugg-Version-1017',
						'SBRAzSugg-Cloud Local State-1018',
						'SBRAzSugg-Cloud Delete State-1019',
						'zAsset-Highlight Visibility Score-1020',
						'zMedAnlyAstAttr-Media Analysis Version-1021',
						'zMedAnlyAstAttr-Audio Classification-1022',
						'zMedAnlyAstAttr-Best Video Range Duration Time Scale-1023',
						'zMedAnlyAstAttr-Best Video Range Start Time Scale-1024',
						'zMedAnlyAstAttr-Best Video Range Duration Value-1025',
						'zMedAnlyAstAttr-Best Video Range Start Value-1026',
						'zMedAnlyAstAttr-Packed Best Playback Rect-1027',
						'zMedAnlyAstAttr-Activity Score-1028',
						'zMedAnlyAstAttr-Video Score-1029',
						'zMedAnlyAstAttr-AutoPlay Suggestion Score-1030',
						'zMedAnlyAstAttr-Blurriness Score-1031',
						'zMedAnlyAstAttr-Exposure Score-1032',
						'zAssetAnalyState-Asset UUID-4TableStart-1033',
						'zAssetAnalyState-Analyisis State-1034',
						'zAssetAnalyState-Worker Flags-1035',
						'zAssetAnalyState-Worker Type-1036',
						('zAssetAnalyState-Ignore Until Date-1037', 'datetime'),
						('zAssetAnalyState-Last Ignored Date-1038', 'datetime'),
						('zAssetAnalyState-Sort Token-1039', 'datetime'),
						'zAsset-Overall Aesthetic Score-1040',
						'zCompAssetAttr-Behavioral Score-1041',
						'zCompAssetAttr-Failure Score zCompAssetAttr-1042',
						'zCompAssetAttr-Harmonious Color Score-1043',
						'zCompAssetAttr-Immersiveness Score-1044',
						'zCompAssetAttr-Interaction Score-1045',
						'zCompAssetAttr-Intersting Subject Score-1046',
						'zCompAssetAttr-Intrusive Object Presence Score-1047',
						'zCompAssetAttr-Lively Color Score-1048',
						'zCompAssetAttr-Low Light-1049',
						'zCompAssetAttr-Noise Score-1050',
						'zCompAssetAttr-Pleasant Camera Tilt Score-1051',
						'zCompAssetAttr-Pleasant Composition Score-1052',
						'zCompAssetAttr-Pleasant Lighting Score-1053',
						'zCompAssetAttr-Pleasant Pattern Score-1054',
						'zCompAssetAttr-Pleasant Perspective Score-1055',
						'zCompAssetAttr-Pleasant Post Processing Score-1056',
						'zCompAssetAttr-Pleasant Reflection Score-1057',
						'zCompAssetAttrPleasant Symmetry Score-1058',
						'zCompAssetAttr-Sharply Focused Subject Score-1059',
						'zCompAssetAttr-Tastfully Blurred Score-1060',
						'zCompAssetAttr-Well Chosen Subject Score-1061',
						'zCompAssetAttr-Well Framed Subject Score-1062',
						'zCompAssetAttr-Well Timeed Shot Score-1063',
						'zCldRes-Asset UUID-4TableStart-1064',
						'zCldRes-Cloud Local State-1065',
						'zCldRes-File Size-1066',
						'zCldRes-Height-1067',
						'zCldRes-Is Available-1068',
						'zCldRes-Is Locally Available-1069',
						'zCldRes-Prefetch Count-1070',
						'zCldRes-Source Type-1071',
						'zCldRes-Type-1072',
						'zCldRes-Width-1073',
						('zCldRes-Date Created-1074', 'datetime'),
						('zCldRes-Last OnDemand Download Date-1075', 'datetime'),
						('zCldRes-Last Prefetch Date-1076', 'datetime'),
						'zCldRes-Prunedat-1077',
						'zCldRes-File Path-1078',
						'zCldRes-Fingerprint-1079',
						'zCldRes-Item ID-1080',
						'zCldRes-UniID-1081',
						'zAddAssetAttr-zPK-1082',
						'zAddAssetAttr-zENT-1083',
						'ZAddAssetAttr-zOPT-1084',
						'zAddAssetAttr-zAsset= zAsset_zPK-1085',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-1086',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-1087',
						'zAddAssetAttr-Master Fingerprint-1088',
						'zAddAssetAttr-Public Global UUID-1089',
						'zAddAssetAttr-Deferred Photo Identifier-1090',
						'zAddAssetAttr-Original Assets UUID-1091',
						'zAddAssetAttr-Import Session ID-1092',
						'zAddAssetAttr-Originating Asset Identifier-1093',
						'zAddAssetAttr.Adjusted Fingerprint-1094',
						'zAlbumList-zPK= Album List Key-1095',
						'zAlbumList-zENT-1096',
						'zAlbumList-zOPT-1097',
						'zAlbumList-ID Key-1098',
						'zAlbumList-UUID-1099',
						'zAsset-zPK-1100',
						'zAsset-zENT-1101',
						'zAsset-zOPT-1102',
						'zAsset-Master= zCldMast-zPK-1103',
						'zAsset-Extended Attributes= zExtAttr-zPK-1104',
						'zAsset-Import Session Key-1105',
						'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-1106',
						'zAsset-FOK-Cloud Feed Asset Entry Key-1107',
						'zAsset-Moment Share Key= zShare-zPK-1108',
						'zAsset-zMoment Key= zMoment-zPK-1109',
						'zAsset-Computed Attributes Asset Key-1110',
						'zAsset-Highlight Being Assets-HBA Key-1111',
						'zAsset-Highlight Being Extended Assets-HBEA Key-1112',
						'zAsset-Highligh Being Summary Assets-HBSA Key-1113',
						'zAsset-Day Group Highlight Being Assets-DGHBA Key-1114',
						'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key-1115',
						'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key-1116',
						'zAsset-Promotion Score-1117',
						'zAsset-Media Analysis Attributes Key-1118',
						'zAsset-Media Group UUID-1119',
						'zAsset-UUID = store.cloudphotodb-1120',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-1121',
						'zAsset.Cloud Collection GUID-1122',
						'zAsset-Avalanche UUID-1123',
						'zAssetAnalyState-zPK-1124',
						'zAssetAnalyState-zEnt-1125',
						'zAssetAnalyState-zOpt-1126',
						'zAssetAnalyState-Asset= zAsset-zPK-1127',
						'zAssetAnalyState-Asset UUID-1128',
						'zAssetDes-zPK-1129',
						'zAssetDes-zENT-1130',
						'zAssetDes-zOPT-1131',
						'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK-1132',
						'zCldFeedEnt-zPK= zCldShared keys-1133',
						'zCldFeedEnt-zENT-1134',
						'zCldFeedEnt-zOPT-1135',
						'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-1136',
						'zCldFeedEnt-Entry Invitation Record GUID-1137',
						'zCldFeedEnt-Entry Cloud Asset GUID-1138',
						'zCldMast-zPK= zAsset-Master-1139',
						'zCldMast-zENT-1140',
						'zCldMast-zOPT-1141',
						'zCldMast-Moment Share Key= zShare-zPK-1142',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-1143',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-1144',
						'zCldMast-Originating Asset ID-1145',
						'zCldMast-Import Session ID- AirDrop-StillTesting-1146',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-1147',
						'CMzCldMastMedData-zENT-1148',
						'CMzCldMastMedData-zOPT-1149',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-1150',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-1151',
						'AAAzCldMastMedData-zENT-1152',
						'AAAzCldMastMedData-zOPT-1153',
						'AAAzCldMastMedData-CldMast key-1154',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-1155',
						'zCldRes-zPK-1156',
						'zCldRes-zENT-1157',
						'zCldRes-zOPT-1158',
						'zCldRes-Asset= zAsset-zPK-1159',
						'zCldRes-Cloud Master= zCldMast-zPK-1160',
						'zCldRes-Asset UUID-1161',
						'zCldShareAlbumInvRec-zPK-1162',
						'zCldShareAlbumInvRec-zEnt-1163',
						'zCldShareAlbumInvRec-zOpt-1164',
						'zCldShareAlbumInvRec-Album Key-1165',
						'zCldShareAlbumInvRec-FOK Album Key-1166',
						'zCldShareAlbumInvRec-Album GUID-1167',
						'zCldShareAlbumInvRec-Cloud GUID-1168',
						'zCldSharedComment-zPK-1169',
						'zCldSharedComment-zENT-1170',
						'zCldSharedComment-zOPT-1171',
						'zCldSharedComment-Commented Asset Key= zAsset-zPK-1172',
						'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-1173',
						'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-1174',
						'zCldSharedComment-Liked Asset Key= zAsset-zPK-1175',
						'zCldSharedComment-CldFeedLikeCommentEntry Key-1176',
						'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-1177',
						'zCldSharedComment-Cloud GUID-1178',
						'zCompAssetAttr-zPK-1179',
						'zCompAssetAttr-zEnt-1180',
						'zCompAssetAttr-zOpt-1181',
						'zCompAssetAttr-Asset Key-1182',
						'zDetFace-zPK-1183',
						'zDetFace-zEnt-1184',
						'zDetFace.zOpt-1185',
						'zDetFace-Asset= zAsset-zPK or Asset Containing Face-1186',
						'zDetFace-Person= zPerson-zPK-1187',
						'zDetFace-Person Being Key Face-1188',
						'zDetFace-Face Print-1189',
						'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-1190',
						'zDetFace-FaceGroup= zDetFaceGroup-zPK-1191',
						'zDetFace-UUID-1192',
						'zDetFaceGroup-zPK-1193',
						'zDetFaceGroup-zENT-1194',
						'zDetFaceGroup-zOPT-1195',
						'zDetFaceGroup-AssocPerson= zPerson-zPK-1196',
						'zDetFaceGroup-KeyFace= zDetFace-zPK-1197',
						'zDetFaceGroup-UUID-1198',
						'zDetFacePrint-zPK-1199',
						'zDetFacePrint-zEnt-1200',
						'zDetFacePrint-zOpt-1201',
						'zDetFacePrint-Face Key-1202',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-1203',
						'zExtAttr-zENT-1204',
						'zExtAttr-zOPT-1205',
						'zExtAttr-Asset Key-1206',
						'zFaceCrop-zPK-1207',
						'zFaceCrop-zEnt-1208',
						'zFaceCrop-zOpt-1209',
						'zFaceCrop-Asset Key-1210',
						'zFaceCrop-Invalid Merge Canidate Person UUID-1211',
						'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-1212',
						'zFaceCrop-Face Key-1213',
						'zFaceCrop-UUID-1214',
						'zGenAlbum-zPK=26AlbumLists= 26Albums-1215',
						'zGenAlbum-zENT-1216',
						'zGenAlbum-zOpt-1217',
						'zGenAlbum-Key Asset-Key zAsset-zPK-1218',
						'zGenAlbum-Secondary Key Asset-1219',
						'zGenAlbum-Tertiary Key Asset-1220',
						'zGenAlbum-Custom Key Asset-1221',
						'zGenAlbum-Parent Folder Key= zGenAlbum-zPK-1222',
						'zGenAlbum-FOK Parent Folder-1223',
						'zGenAlbum-UUID-1224',
						'zGenAlbum-Cloud_GUID = store.cloudphotodb-1225',
						'zGenAlbum-Project Render UUID-1226',
						'zIntResou-zPK-1227',
						'zIntResou-zENT-1228',
						'zIntResou-zOPT-1229',
						'zIntResou-Asset= zAsset_zPK-1230',
						'zIntResou-Fingerprint-1231',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-1232',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-1233',
						'zMedAnlyAstAttr-zEnt-1234',
						'zMedAnlyAstAttr-zOpt-1235',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-1236',
						'zPerson-zPK=zDetFace-Person-1237',
						'zPerson-zEnt-1238',
						'zPerson-zOpt-1239',
						'zPerson-KeyFace=zDetFace-zPK-1240',
						'zPerson-Assoc Face Group Key-1241',
						'zPerson-Person UUID-1242',
						'zSceneP-zPK-1243',
						'zSceneP-zENT-1244',
						'zSceneP-zOPT-1245',
						'zShare-zPK-1246',
						'zShare-zENT-1247',
						'zShare-zOPT-1248',
						'zShare-UUID-1249',
						'SPLzShare-UUID-1250',
						'zShare-Scope ID = store.cloudphotodb-1251',
						'zSharePartic-zPK-1252',
						'zSharePartic-zENT-1253',
						'zSharePartic-zOPT-1254',
						'zSharePartic-Share Key= zShare-zPK-1255',
						'zSharePartic-UUID-1256',
						'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key-1257',
						'zUnmAdj-zOPT-1258',
						'zUnmAdj-zENT-1259',
						'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK-1260',
						'zUnmAdj-UUID-1261',
						'zUnmAdj-Other Adjustments Fingerprint-1262',
						'zUnmAdj-Similar to Orig Adjustments Fingerprint-1263',
						'z25AlbumList-25Albums= zGenAlbum-zPK-1264',
						'z25AlbumList-Album List Key-1265',
						'z25AlbumList-FOK25Albums Key-1266',
						'z26Assets-26Albums= zGenAlbum-zPK-1267',
						'z26Assets-3Asset Key= zAsset-zPK in the Album-1268',
						'z26Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY-1269')
		data_list = get_sqlite_db_records(source_path, query)

		return data_headers, data_list, source_path

@artifact_processor
def Ph94_2iOS14RefforAssetAnalysisSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
	for source_path in files_found:
		source_path = str(source_path)

		if source_path.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if (version.parse(iosversion) <= version.parse("13.7")) or (version.parse(iosversion) >= version.parse("15")):
		logfunc("Unsupported version for Syndication.photoslibrary for iOS " + iosversion)
		return (), [], source_path
	if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
		source_path = get_file_path(files_found, "Photos.sqlite")
		if source_path is None or not os.path.exists(source_path):
			logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
			return (), [], source_path
		data_list = []

		query = '''
		SELECT
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		CASE zAsset.ZCOMPLETE
			WHEN 1 THEN '1-Yes-1'
		END AS 'zAsset Complete',
		zAsset.Z_PK AS 'zAsset-zPK-4QueryStart',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK-4QueryStart',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb-4QueryStart',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint-4TableStart',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint-4TableStart',
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
			WHEN 3 THEN '3-LPLPs-Asset_or_SWYPs-Asset_NoAuto-Display-3'
			WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
			WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
			WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
			WHEN 7 THEN '7-StillTesting-7'
			WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
			WHEN 12 THEN '12-SWY-Syndicaion-PL-Asset_Auto-Display_In_LPL-12'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
		END AS 'zAsset-Saved Asset Type',
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
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
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID-4QueryStart',
		DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Alt Import Image Date',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting- 4QueryStart',
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
		ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID-4QueryStart',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4QueryStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4QueryStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4QueryStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4QueryStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4QueryStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4QueryStart',
		CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'ParentzGenAlbum-Cloud-Local-State-4QueryStart',
		CASE zGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'zGenAlbum-Cloud_Local_State-4QueryStart',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Cloud Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Start Date- 4QueryStart',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- End Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date- 4QueryStart',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title- 4QueryStart',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied- 4QueryStart',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY- 4QueryStart',
		zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle ID- 4QueryStart',
		CASE zGenAlbum.Z_ENT
			WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
			WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
			WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
			WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
			WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
		END AS 'zGenAlbum-zENT- Entity- 4QueryStart',
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
		END AS 'ParentzGenAlbum- Kind- 4QueryStart',
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
		END AS 'zGenAlbum-Album Kind- 4QueryStart',		
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
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID-4TableStart',
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
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier-4QueryStart',
		zAddAssetAttr.ZDEFERREDPROCESSINGCANDIDATEOPTIONS AS 'zAddAssetAttr-Deferred Processing Candidate Options',
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		zUnmAdj.ZUUID AS 'zUnmAdj-UUID-4TableStart',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		DateTime(zUnmAdj.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zUnmAdj-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
		zUnmAdj.ZEDITORLOCALIZEDNAME AS 'zUnmAdj-Editor Localized Name',
		zUnmAdj.ZADJUSTMENTFORMATIDENTIFIER AS 'zUnmAdj-Adjustment Format ID',
		zAddAssetAttr.ZMONTAGE AS 'zAddAssetAttr-Montage',
		CASE zUnmAdj.ZADJUSTMENTRENDERTYPES
			WHEN 0 THEN '0-Standard or Portrait with erros-0'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Portrait-2'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTRENDERTYPES || ''
		END AS 'zUnmAdj-Adjustment Render Types',
		CASE zUnmAdj.ZADJUSTMENTFORMATVERSION
			WHEN 1.0 THEN '1.0-Markup-1.0'
			WHEN 1.1 THEN '1.1-Slow-Mo-1.1'
			WHEN 1.2 THEN '1.2-StillTesting'
			WHEN 1.3 THEN '1.3-StillTesting'
			WHEN 1.4 THEN '1.4-Filter-1.4'
			WHEN 1.5 THEN '1.5-Adjust-1.5'
			WHEN 1.6 THEN '1.6-Video-Trim-1.6'
			WHEN 1.7 THEN '1.7-StillTesting'
			WHEN 1.8 THEN '1.8-StillTesting'
			WHEN 1.9 THEN '1.9-StillTesting'
			WHEN 2.0 THEN '2.0-ScreenshotServices-2.0'
			ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTFORMATVERSION || ''
		END AS 'zUnmAdj-Adjustment Format Version',
		zUnmAdj.ZADJUSTMENTBASEIMAGEFORMAT AS 'zUnmAdj-Adjustment Base Image Format',
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
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type-4TableStart',
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
		zShare.ZTHUMBNAILIMAGEDATA AS 'zShare-Thumbnail Image Data',
		SPLzShare.ZTHUMBNAILIMAGEDATA AS 'SPLzShare-Thumbnail Image Data',
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
		zAddAssetAttr.ZORIGINALRESOURCECHOICE AS 'zAddAssetAttr-Orig Resource Choice',
		zAddAssetAttr.ZSPATIALOVERCAPTUREGROUPIDENTIFIER AS 'zAddAssetAttr-Spatial Over Capture Group ID',
		zAddAssetAttr.ZPLACEANNOTATIONDATA AS 'zAddAssetAttr-Place Annotation Data',
		zAddAssetAttr.ZDISTANCEIDENTITY AS 'zAddAssetAttr-Distance Identity',
		zAddAssetAttr.ZEDITEDIPTCATTRIBUTES AS 'zAddAssetAttr-Edited IPTC Attributes',
		zAssetDes.ZLONGDESCRIPTION AS 'zAssetDes-Long Description',
		zAddAssetAttr.ZASSETDESCRIPTION AS 'zAddAssetAttr-Asset Description',
		zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
		zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
		zAddAssetAttr.ZPHOTOSTREAMTAGID AS 'zAddAssetAttr-Photo Stream Tag ID',
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
		zCldSharedComment.ZCOMMENTTYPE AS 'zCldSharedComment-Type',
		zCldSharedComment.ZCOMMENTTEXT AS 'zCldSharedComment-Comment Text',
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
		CASE zAddAssetAttr.ZSHARETYPE
			WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
			WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
		END AS 'zAddAssetAttr-Share Type',
		zShare.ZUUID AS 'zShare-UUID-CMM-4TableStart',
		SPLzShare.ZUUID AS 'SPLzShare-UUID-SPL-4TableStart',
		CASE zShare.Z_ENT
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
		END AS 'zShare-zENT-CMM',
		CASE SPLzShare.Z_ENT
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.Z_ENT || ''
		END AS 'SPLzShare-zENT-SPL',
		CASE zShare.ZSTATUS
			WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
		END AS 'zShare-Status-CMM',
		CASE SPLzShare.ZSTATUS
			WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSTATUS || ''
		END AS 'SPLzShare-Status-SPL',
		CASE zShare.ZSCOPETYPE
			WHEN 2 THEN '2-iCloudLink-CMMoment-2'
			WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
		END AS 'zShare-Scope Type-CMM',
		CASE SPLzShare.ZSCOPETYPE
			WHEN 2 THEN '2-iCloudLink-CMMoment-2'
			WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSCOPETYPE || ''
		END AS 'SPLzShare-Scope Type-SPL',
		CASE zShare.ZLOCALPUBLISHSTATE
			WHEN 2 THEN '2-Published-2'
			ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
		END AS 'zShare-Local Publish State-CMM',
		CASE SPLzShare.ZLOCALPUBLISHSTATE
			WHEN 2 THEN '2-Published-2'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZLOCALPUBLISHSTATE || ''
		END AS 'SPLzShare-Local Publish State-SPL',
		CASE zShare.ZPUBLICPERMISSION
			WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
			WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
			ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
		END AS 'zShare-Public Permission-CMM',
		CASE SPLzShare.ZPUBLICPERMISSION
			WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
			WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZPUBLICPERMISSION || ''
		END AS 'SPLzShare-Public Permission-SPL',
		zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID-CMM',
		SPLzShare.ZORIGINATINGSCOPEIDENTIFIER AS 'SPLzShare-Originating Scope ID-SPL',
		zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID-CMM',
		SPLzShare.ZSCOPEIDENTIFIER AS 'SPLzShare-Scope ID-SPL',
		zShare.ZTITLE AS 'zShare-Title-CMM',
		SPLzShare.ZTITLE AS 'SPLzShare-Title-SPL',
		zShare.ZSHAREURL AS 'zShare-Share URL-CMM',
		SPLzShare.ZSHAREURL AS 'SPLzShare-Share URL-SPL',
		DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date-CMM',
		DateTime(SPLzShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Creation Date-SPL',
		DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date-CMM',
		DateTime(SPLzShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Start Date-SPL',
		DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date-CMM',
		DateTime(SPLzShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-End Date-SPL',
		DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date-CMM',
		DateTime(SPLzShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Expiry Date-SPL',
		zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
		SPLzShare.ZASSETCOUNT AS 'SPLzShare-Asset Count-SPL',
		zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
		SPLzShare.ZPHOTOSCOUNT AS 'SPLzShare-Photos Count-CMM-SPL',
		zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
		SPLzShare.ZUPLOADEDPHOTOSCOUNT AS 'SPLzShare-Uploaded Photos Count-SPL',
		zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
		SPLzShare.ZVIDEOSCOUNT AS 'SPLzShare-Videos Count-SPL',
		zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
		SPLzShare.ZUPLOADEDVIDEOSCOUNT AS 'SPLzShare-Uploaded Videos Count-SPL',
		zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',
		SPLzShare.ZFORCESYNCATTEMPTED AS 'SPLzShare-Force Sync Attempted-SPL',
		CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-CMM-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'zShare-Should Notify On Upload Completion-CMM',
		CASE SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-SPL-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'SPLzShare-Should Notify On Upload Completion-SPL',
		CASE zShare.ZTRASHEDSTATE
			WHEN 0 THEN '0-Not_in_Trash-0'
			WHEN 1 THEN '1-In_Trash-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
		END AS 'zShare-Trashed State-CMM',
		CASE SPLzShare.ZTRASHEDSTATE
			WHEN 0 THEN '0-Not_in_Trash-0'
			WHEN 1 THEN '1-In_Trash-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZTRASHEDSTATE || ''
		END AS 'SPLzShare-Trashed State-SPL',
		CASE zShare.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Not Deleted-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
		END AS 'zShare-Cloud Delete State-CMM',
		CASE SPLzShare.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-Not Deleted-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZCLOUDDELETESTATE || ''
		END AS 'SPLzShare-Cloud Delete State-SPL',
		CASE zShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'zShare-Should Ignor Budgets-CMM',
		CASE SPLzShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'SPLzShare-Should Ignor Budgets-SPL',
		zSharePartic.ZUUID AS 'zSharePartic-UUID-4TableStart',
		SPLzSharePartic.ZUUID AS 'SPLzSharePartic-UUID-4TableStart',
		CASE zSharePartic.ZACCEPTANCESTATUS
			WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
			WHEN 2 THEN '2-Invite-Accepted-2'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
		END AS 'zSharePartic-Acceptance Status',
		CASE SPLzSharePartic.ZACCEPTANCESTATUS
			WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
			WHEN 2 THEN '2-Invite-Accepted-2'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZACCEPTANCESTATUS || ''
		END AS 'SPLzSharePartic-Acceptance Status',
		CASE zSharePartic.ZISCURRENTUSER
			WHEN 0 THEN '0-Participant-Not_CloudStorageOwner-0'
			WHEN 1 THEN '1-Participant-Is_CloudStorageOwner-1'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
		END AS 'zSharePartic-Is Current User',
		CASE SPLzSharePartic.ZISCURRENTUSER
			WHEN 0 THEN '0-Participant-Not_CloudStorageOwner-0'
			WHEN 1 THEN '1-Participant-Is_CloudStorageOwner-1'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
		END AS 'SPLzSharePartic-Is Current User',
		CASE zSharePartic.ZROLE
			WHEN 1 THEN '1-Participant-is-Owner-Role-1'
			WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
		END AS 'zSharePartic-Role',
		CASE SPLzSharePartic.ZROLE
			WHEN 1 THEN '1-Participant-is-Owner-Role-1'
			WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
		END AS 'SPLzSharePartic-Role',
		CASE zSharePartic.ZPERMISSION
			WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
		END AS 'zSharePartic-Premission',
		CASE SPLzSharePartic.ZPERMISSION
			WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZPERMISSION || ''
		END AS 'SPLzSharePartic-Premission',
		zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
		SPLzSharePartic.ZUSERIDENTIFIER AS 'SPLzSharePartic-User ID',
		SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK-4TableStart',
		zSharePartic.Z_PK AS 'zSharePartic-zPK-4TableStart',
		zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
		SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
		zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
		SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
		ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID-4TableStart',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4TableStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4TableStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4TableStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4TableStart',
		CASE zAlbumList.ZNEEDSREORDERINGNUMBER
			WHEN 1 THEN '1-Yes-1'
			ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
		END AS 'zAlbumList-Needs Reordering Number',
		CASE zGenAlbum.Z_ENT
			WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
			WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
			WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
			WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
			WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
		END AS 'zGenAlbum-zENT- Entity',
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
		CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'ParentzGenAlbum-Cloud-Local-State',
		CASE zGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'zGenAlbum-Cloud_Local_State',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY',
		zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle ID',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
		ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
		zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',
		CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
			WHEN 1 THEN 'No-1'
			WHEN 24 THEN '24-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
		END AS 'ParentzGenAlbum-Pending Items Type',
		CASE zGenAlbum.ZPENDINGITEMSTYPE
			WHEN 1 THEN 'No-1'
			WHEN 24 THEN '24-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
		END AS 'zGenAlbum-Pending Items Type',
		zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
		zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',
		zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
		ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
		zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',
		CASE zGenAlbum.ZHASUNSEENCONTENT
			WHEN 0 THEN 'No Unseen Content-StillTesting-0'
			WHEN 1 THEN 'Unseen Content-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
		END AS 'zGenAlbum-Has Unseen Content',
		zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',
		CASE zGenAlbum.ZISOWNED
			WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
			WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
		END AS 'zGenAlbum-is Owned',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
			WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
			WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
		END AS 'zGenAlbum-Cloud Relationship State',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
			WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
		END AS 'zGenAlbum-Cloud Relationship State Local',
		zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',
		zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',
		zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',
		zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
		zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',
		zAsset.ZCLOUDOWNERHASHEDPERSONID AS 'zAsset-Cloud Owner Hashed Person ID',
		zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
		END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
		END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
			WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
		END AS 'zGenAlbum-Cloud Album Sub Type',
		DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Contribution Date',
		DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Last Interesting Change Date',
		CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
		END AS 'zGenAlbum-Cloud Notification Enabled',
		CASE ParentzGenAlbum.ZISPINNED
			WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
			WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
		END AS 'ParentzGenAlbum-Pinned',
		CASE zGenAlbum.ZISPINNED
			WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
			WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
		END AS 'zGenAlbum-Pinned',
		CASE ParentzGenAlbum.ZCUSTOMSORTKEY
			WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
			WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
			WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
		END AS 'ParentzGenAlbum-Custom Sort Key',
		CASE zGenAlbum.ZCUSTOMSORTKEY
			WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
			WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
			WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
		END AS 'zGenAlbum-Custom Sort Key',
		CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
			WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
			WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
		END AS 'ParentzGenAlbum-Custom Sort Ascending',
		CASE zGenAlbum.ZCUSTOMSORTASCENDING
			WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
			WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
		END AS 'zGenAlbum-Custom Sort Ascending',
		CASE ParentzGenAlbum.ZISPROTOTYPE
			WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
			WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
		END AS 'ParentzGenAlbum-Is Prototype',
		CASE zGenAlbum.ZISPROTOTYPE
			WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
			WHEN 1 THEN 'zGenAlbum-Prototype-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
		END AS 'zGenAlbum-Is Prototype',
		CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'ParentzGenAlbum-Project Document Type',
		CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'zGenAlbum-Project Document Type',
		CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'ParentzGenAlbum-Custom Query Type',
		CASE zGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'zGenAlbum-Custom Query Type',
		CASE ParentzGenAlbum.ZTRASHEDSTATE
			WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
			WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
		END AS 'ParentzGenAlbum-Trashed State',
		DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
		CASE zGenAlbum.ZTRASHEDSTATE
			WHEN 0 THEN 'zGenAlbum Not In Trash-0'
			WHEN 1 THEN 'zGenAlbum Album In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
		END AS 'zGenAlbum-Trashed State',
		DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
		CASE ParentzGenAlbum.ZCLOUDDELETESTATE
			WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
			WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
		END AS 'ParentzGenAlbum-Cloud Delete State',
		CASE zGenAlbum.ZCLOUDDELETESTATE
			WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
			WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
		END AS 'zGenAlbum-Cloud Delete State',
		CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
			WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
			WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
		END AS 'zGenAlbum-Cloud Owner Whitelisted',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
		END AS 'zGenAlbum-Cloud Local Public URL Enabled',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
			WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
		END AS 'zGenAlbum-Cloud Public URL Enabled',
		zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',
		zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',
		zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',
		zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',
		zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
		zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
		CASE zCldShareAlbumInvRec.ZISMINE
			WHEN 0 THEN 'Not My Invitation-0'
			WHEN 1 THEN 'My Invitation-1'
			ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
		END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
		CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
			WHEN 0 THEN '0-StillTesting-0'
			WHEN 1 THEN '1-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
		END AS 'zCldShareAlbumInvRec-Invitation State Local',
		CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
			WHEN 1 THEN 'Shared Album Invitation Pending-1'
			WHEN 2 THEN 'Shared Album Invitation Accepted-2'
			WHEN 3 THEN 'Shared Album Invitation Declined-3'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
		END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
		DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldShareAlbumInvRec-Subscription Date',
		zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
		zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
		zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
		zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
		zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',
		zGenAlbum.ZKEYASSETFACEIDENTIFIER AS 'zGenAlbum-Key Asset Face ID',
		CASE
			WHEN zAsset.ZFACEAREAPOINTS > 0 THEN 'Face Area Points Detected in zAsset'
			ELSE 'Face Area Points Not Detected in zAsset'
		END AS 'zFaceCrop-Face Area Points',
		zAsset.ZFACEADJUSTMENTVERSION AS 'zAsset-Face Adjustment Version',
		CASE zDetFace.ZASSETVISIBLE
			WHEN 0 THEN 'Asset Not Visible Photo Library-0'
			WHEN 1 THEN 'Asset Visible Photo Library-1'
			ELSE 'Unknown-New-Value!: ' || zDetFace.ZASSETVISIBLE || ''
		END AS 'zDetFace-Asset Visible',
		zPerson.ZFACECOUNT AS 'zPerson-Face Count',
		zDetFace.ZFACECROP AS 'zDetFace-Face Crop',
		zDetFace.ZFACEALGORITHMVERSION AS 'zDetFace-Face Algorithm Version',
		zDetFace.ZADJUSTMENTVERSION AS 'zDetFace-Adjustment Version',
		zDetFace.ZUUID AS 'zDetFace-UUID-4TableStart',
		zPerson.ZPERSONUUID AS 'zPerson-Person UUID-4TableStart',
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
			WHEN 2 THEN '2-Verified-Has-Person-URI'
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
		zFaceCrop.ZUUID AS 'zFaceCrop-UUID-4TableStart',
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
			WHEN 1 THEN 'Infant-Toddler Age Type-1'
			WHEN 2 THEN 'Toddler-Child Age Type-2'
			WHEN 3 THEN 'Child-Young Adult Age Type-3'
			WHEN 4 THEN 'Young Adult-Adult Age Type-4'
			WHEN 5 THEN 'Adult-5'
			ELSE 'Unknown-New-Value!: ' || zPerson.ZAGETYPE || ''
		END AS 'zPerson-Age Type Estimate',
		CASE zDetFace.ZAGETYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Infant-Toddler Age Type-1'
			WHEN 2 THEN 'Toddler-Child Age Type-2'
			WHEN 3 THEN 'Child-Young Adult Age Type-3'
			WHEN 4 THEN 'Young Adult-Adult Age Type-4'
			WHEN 5 THEN 'Adult-5'
			ELSE 'Unknown-New-Value!: ' || zDetFace.ZAGETYPE || ''
		END AS 'zDetFace-Age Type Estimate',
		CASE zDetFace.ZHAIRCOLORTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Black-Brown Hair Color-1'
			WHEN 2 THEN 'Brown-Blonde Hair Color-2'
			WHEN 3 THEN 'Brown-Red Hair Color-3'
			WHEN 4 THEN 'Red-White Hair Color-4'
			WHEN 5 THEN 'StillTesting-Artifical-5'
			WHEN 6 THEN 'White-Bald Hair Color-6'
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
		END AS 'zDetFace-Hidden-Asset Hidden',
		CASE zDetFace.ZISINTRASH
			WHEN 0 THEN 'Not In Trash-0'
			WHEN 1 THEN 'In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zDetFace.ZISINTRASH || ''
		END AS 'zDetFace-In Trash-Recently Deleted',
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
		zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID-4TableStart',
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
		zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID-4TableStart',
		zMemory.Z_PK AS 'zMemory-zPK',
		z3MemoryBCAs.Z_3CURATEDASSETS AS 'z3MemoryBCAs-3CuratedAssets = zAsset-zPK',
		z3MemoryBCAs.Z_40MEMORIESBEINGCURATEDASSETS AS 'z3MemoryBCAs-40MemoriesBeingCuratedAssets = zMemory-zPK',
		z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-3ExtCuratedAssets = zAsset-zPK',
		z3MemoryBECAs.Z_40MEMORIESBEINGEXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-40MemoriesBeingExtCuratedAssets = zMemory-zPK',
		z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AS 'z3MemoryBMCAs-3MovieCuratedAssets = zAsset-zPK',
		z3MemoryBMCAs.Z_40MEMORIESBEINGMOVIECURATEDASSETS AS 'z3MemoryBMCAs-40MemoriesBeingMovieCuratedAssets = zMemory-zPK',
		z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AS 'z3MemoryBRAs-3RepresentativeAssets = zAsset-zPK',
		z3MemoryBRAs.Z_40MEMORIESBEINGREPRESENTATIVEASSETS AS 'z3MemoryBRAs-40RepresentativeAssets = zMemory-zPK',
		zMemory.ZKEYASSET AS 'zMemory-Key Asset = zAsset-zPK',
		zMemory.ZUUID AS 'zMemory-UUID',
		zMemory.ZSUBTITLE AS 'zMemory-SubTitle',
		zMemory.ZTITLE AS 'zMemory-Title',
		CASE zMemory.ZCATEGORY
			WHEN 1 THEN '1-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 8 THEN '8-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 17 THEN '17-StillTesting'
			WHEN 19 THEN '19-StillTesting'
			WHEN 21 THEN '21-StillTesting'
			WHEN 201 THEN '201-StillTesting'
			WHEN 203 THEN '203-StillTesting'
			WHEN 204 THEN '204-StillTesting'
			WHEN 211 THEN '211-StillTesting'
			WHEN 217 THEN '217-StillTesting'
			WHEN 220 THEN '220-StillTesting'
			WHEN 301 THEN '301-StillTesting'
			WHEN 302 THEN '302-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZCATEGORY || ''
		END AS 'zMemory-Category',
		CASE zMemory.ZSUBCATEGORY
			WHEN 0 THEN '0-StillTesting'
			WHEN 201 THEN '201-StillTesting'
			WHEN 204 THEN '204-StillTesting'
			WHEN 206 THEN '206-StillTesting'
			WHEN 207 THEN '207-StillTesting'
			WHEN 212 THEN '212-StillTesting'
			WHEN 213 THEN '213-StillTesting'
			WHEN 214 THEN '214-StillTesting'
			WHEN 402 THEN '402-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSUBCATEGORY || ''
		END AS 'zMemory-SubCategory',
		DateTime(zMemory.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Creation Date',
		CASE zMemory.ZUSERCREATED
			WHEN 0 THEN 'Memory Not User Created-0'
			WHEN 1 THEN 'Memory User Created-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZUSERCREATED || ''
		END AS 'zMemory-User Created',
		CASE zMemory.ZFAVORITE
			WHEN 0 THEN 'Memory Not Favorite-0'
			WHEN 1 THEN 'Memory Favorite-1'
		END AS 'zMemory-Favorite Memory',
		zMemory.ZSCORE AS 'zMemory-Score',
		zMemory.ZVIEWCOUNT AS 'zMemory-View Count',
		zMemory.ZPLAYCOUNT AS 'zMemory-Play Count',
		zMemory.ZREJECTED AS 'zMemory-Rejected',
		zMemory.ZSHARECOUNT AS 'zMemory-Share Count',
		DateTime(zMemory.ZLASTMOVIEPLAYEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Movie Play Date',
		DateTime(zMemory.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Viewed Date',
		CASE zMemory.ZPENDING
			WHEN 0 THEN 'No-0'
			WHEN 1 THEN 'Yes-1'
			WHEN 2 THEN '2-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZPENDING || ''
		END AS 'zMemory-Pending',
		zMemory.ZPENDINGPLAYCOUNT AS 'zMemory-Pending Play Count Memory',
		zMemory.ZPENDINGSHARECOUNT AS 'zMemory-Pending Share Count Memory',
		zMemory.ZPENDINGVIEWCOUNT AS 'zMemory-Pending View Count Memory',
		CASE zMemory.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZFEATUREDSTATE || ''
		END AS 'zMemory-Featured State',
		zMemory.ZPHOTOSGRAPHVERSION AS 'zMemory-Photos Graph Version',
		zMemory.ZASSETLISTPREDICATE AS 'zMemory-AssetListPredicte',
		CASE zMemory.ZNOTIFICATIONSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZNOTIFICATIONSTATE || ''
		END AS 'zMemory-Notification State',
		CASE zMemory.ZCLOUDLOCALSTATE
			WHEN 0 THEN 'Memory Not Synced with Cloud-0'
			WHEN 1 THEN 'Memory Synced with Cloud-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZCLOUDLOCALSTATE || ''
		END AS 'zMemory-Cloud Local State',
		CASE zMemory.ZCLOUDDELETESTATE
			WHEN 0 THEN 'Memory Not Deleted-0'
			WHEN 1 THEN 'Memory Deleted-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZCLOUDDELETESTATE || ''
		END AS 'zMemory-Cloud Delete State',
		YearzMomentList.ZUUID AS 'YearzMomentList-UUID',
		YearzMomentList.Z_PK AS 'YearzMomentList-zPK',
		zMoment.ZYEARMOMENTLIST AS 'zMoment-Year Moment List',
		YearzMomentList.ZSORTINDEX AS 'YearzMomentList-Sort Index',
		CASE YearzMomentList.ZGRANULARITYLEVEL
			WHEN 10 THEN 'Year and Month Moment-10'
			WHEN 20 THEN 'Year Moment-20'
			ELSE 'Unknown-New-Value!: ' || YearzMomentList.ZGRANULARITYLEVEL || ''
		END AS 'YearzMomentList-Granularity Level',
		DateTime(YearzMomentList.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YearzMomentList-Start Date',
		DateTime(YearzMomentList.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'YearzMomentList-Representative Date',
		DateTime(YearzMomentList.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YearzMomentList-End Date',
		CASE YearzMomentList.ZTRASHEDSTATE
			WHEN 0 THEN 'YearzMomentList Not In Trash-0'
			WHEN 1 THEN 'YearzMomentList In Trash-1'
			ELSE 'Unknown-New-Value!: ' || YearzMomentList.ZTRASHEDSTATE || ''
		END AS 'YearzMomentList-Trashed State',
		MegaYMzMomentList.ZUUID AS 'MegaYMzMomentList-UUID',
		MegaYMzMomentList.Z_PK AS 'MegaYMzMomentList-zPK',
		zMoment.ZMEGAMOMENTLIST AS 'zMoment-Mega Moment List',
		MegaYMzMomentList.ZSORTINDEX AS 'MegaYMzMomentList-Sort Index',
		CASE MegaYMzMomentList.ZGRANULARITYLEVEL
			WHEN 10 THEN 'Year and Month Moment-10'
			WHEN 20 THEN 'Year Moment-20'
			ELSE 'Unknown-New-Value!: ' || MegaYMzMomentList.ZGRANULARITYLEVEL || ''
		END AS 'MegaYMzMomentList-Granularity Level',
		DateTime(MegaYMzMomentList.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'MegaYMzMomentList-Start Date',
		DateTime(MegaYMzMomentList.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'MegaYMzMomentList-Representative Date',
		DateTime(MegaYMzMomentList.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'MegaYMzMomentList-End Date',
		CASE MegaYMzMomentList.ZTRASHEDSTATE
			WHEN 0 THEN 'MegaYMzMomentList Not In Trash-0'
			WHEN 1 THEN 'MegaYMzMomentList In Trash-1'
			ELSE 'Unknown-New-Value!: ' || MegaYMzMomentList.ZTRASHEDSTATE || ''
		END AS 'MegaYMzMomentList-Trashed State',
		zMoment.ZUUID AS 'zMoment-UUID',
		zMoment.Z_PK AS 'zMoment-zPK',
		zMoment.ZAGGREGATIONSCORE AS 'zMoment-Aggregation Score',
		DateTime(zMoment.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Start Date',
		DateTime(zMoment.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Representative Date',
		zMoment.ZTIMEZONEOFFSET AS 'zMoment-Timezone Offset',
		DateTime(zMoment.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Modification Date',
		DateTime(zMoment.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-End Date',
		zMoment.ZSUBTITLE AS 'zMoment-SubTitle',
		zMoment.ZTITLE AS 'zMoment-Title',
		CASE zMoment.ZPROCESSEDLOCATION
			WHEN 2 THEN 'No-2'
			WHEN 3 THEN 'Yes-3'
			WHEN 6 THEN 'Yes-6'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZPROCESSEDLOCATION || ''
		END AS 'zMoment-Processed Location',
		zMoment.ZAPPROXIMATELATITUDE AS 'zMoment-Approx Latitude',
		zMoment.ZAPPROXIMATELONGITUDE AS 'zMoment-Approx Longitude',
		CASE zMoment.ZGPSHORIZONTALACCURACY
			WHEN -1.0 THEN '-1.0'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZGPSHORIZONTALACCURACY || ''
		END AS 'zMoment-GPS Horizontal Accuracy',
		zMoment.ZCACHEDCOUNT AS 'zMoment-Cache Count',
		zMoment.ZCACHEDPHOTOSCOUNT AS 'zMoment-Cached Photos Count',
		zMoment.ZCACHEDVIDEOSCOUNT AS 'zMoment-Cached Videos Count',
		CASE zMoment.ZTRASHEDSTATE
			WHEN 0 THEN 'zMoment Not In Trash-0'
			WHEN 1 THEN 'zMoment In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZTRASHEDSTATE || ''
		END AS 'zMoment-Trashed State',
		zMoment.ZHIGHLIGHT AS 'zMoment-Highlight Key',
		zAsset.ZHIGHLIGHTVISIBILITYSCORE AS 'zAsset-Highlight Visibility Score',
		YearParzPhotosHigh.ZUUID AS 'YearParzPhotosHigh-UUID',
		YearParzPhotosHigh.Z_PK AS 'YearParzPhotosHigh-zPK',
		YearParzPhotosHigh.Z_ENT AS 'YearParzPhotosHigh-zENT',
		YearParzPhotosHigh.Z_OPT AS 'YearParzPhotosHigh-zOPT',
		YearParzPhotosHigh.ZPROMOTIONSCORE AS 'YearParzPhotosHigh-Promotion Score',
		YearParzPhotosHigh.ZTITLE AS 'YearParzPhotosHigh-Title',
		YearParzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'YearParzPhotosHigh-Verbose Smart Description',
		DateTime(YearParzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YearParzPhotosHigh-Start Date',
		DateTime(YearParzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YearParzPhotosHigh-End Date',
		YearParzPhotosHigh.ZYEARKEYASSET AS 'YearParzPhotosHigh-Year Key Asset',
		CASE YearParzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZISCURATED || ''
		END AS 'YearParzPhotosHigh-Is Curated',
		CASE YearParzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZKIND || ''
		END AS 'YearParzPhotosHigh-Kind',
		CASE YearParzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZCATEGORY || ''
		END AS 'YearParzPhotosHigh-Category',
		CASE YearParzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-Visible via For You'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'YearParzPhotosHigh-Visibility State',
		CASE YearParzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YearParzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'YearParzPhotosHigh-Enrichment State',
		YearParzPhotosHigh.ZENRICHMENTVERSION AS 'YearParzPhotosHigh-Enrichment Version',
		YearParzPhotosHigh.ZHIGHLIGHTVERSION AS 'YearParzPhotosHigh-Highlight Version',
		YMParzPhotosHigh.ZUUID AS 'YMParzPhotosHigh-UUID',
		YMParzPhotosHigh.Z_PK AS 'YMParzPhotosHigh-zPK',
		YMParzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'YMParzPhotosHigh-Parent PH Key',
		YMParzPhotosHigh.Z_ENT AS 'YMParzPhotosHigh-zENT',
		YMParzPhotosHigh.Z_OPT AS 'YMParzPhotosHigh-zOPT',
		YMParzPhotosHigh.ZPROMOTIONSCORE AS 'YMParzPhotosHigh-Promotion Score',
		YMParzPhotosHigh.ZTITLE AS 'YMParzPhotosHigh-Title',
		YMParzPhotosHigh.ZSUBTITLE AS 'YMParzPhotosHigh-Subtitle',
		YMParzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'YMParzPhotosHigh-Verbose Smart Description',
		DateTime(YMParzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YMParzPhotosHigh-Start Date',
		DateTime(YMParzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YMParzPhotosHigh-End Date',
		YMParzPhotosHigh.ZMONTHFIRSTASSET AS 'YMParzPhotosHigh-Month First Asset',
		YMParzPhotosHigh.ZMONTHKEYASSET AS 'YMParzPhotosHigh-Month Key Asset',
		CASE YMParzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZISCURATED || ''
		END AS 'YMParzPhotosHigh-Is Curated',
		CASE YMParzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZKIND || ''
		END AS 'YMParzPhotosHigh-Kind',
		CASE YMParzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZCATEGORY || ''
		END AS 'YMParzPhotosHigh-Category',
		CASE YMParzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'YMParzPhotosHigh-Visibility State',
		CASE YMParzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YMParzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'YMParzPhotosHigh-Enrichment State',
		YMParzPhotosHigh.ZENRICHMENTVERSION AS 'YMParzPhotosHigh-Enrichment Version',
		YMParzPhotosHigh.ZHIGHLIGHTVERSION AS 'YMParzPhotosHigh-Highlight Version',
		DGParzPhotosHigh.ZUUID AS 'DGParzPhotosHigh-UUID',
		DGParzPhotosHigh.Z_PK AS 'DGParzPhotosHigh-zPK',
		DGParzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGParzPhotosHigh-Parent PH Key',
		DGParzPhotosHigh.Z_ENT AS 'DGParzPhotosHigh-zENT',
		DGParzPhotosHigh.Z_OPT AS 'DGParzPhotosHigh-zOPT',
		DGParzPhotosHigh.ZPROMOTIONSCORE AS 'DGParzPhotosHigh-Promotion Score',
		DGParzPhotosHigh.ZTITLE AS 'DGParzPhotosHigh-Title',
		DGParzPhotosHigh.ZSUBTITLE AS 'DGParzPhotosHigh-Subtitle',
		DGParzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGParzPhotosHigh-Verbose Smart Description',
		DateTime(DGParzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGParzPhotosHigh-Start Date',
		DateTime(DGParzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGParzPhotosHigh-End Date',
		DGParzPhotosHigh.ZMONTHFIRSTASSET AS 'DGParzPhotosHigh-Month First Asset',
		DGParzPhotosHigh.ZMONTHKEYASSET AS 'DGParzPhotosHigh-Month Key Asset',
		CASE DGParzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZISCURATED || ''
		END AS 'DGParzPhotosHigh-Is Curated',
		CASE DGParzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZKIND || ''
		END AS 'DGParzPhotosHigh-Kind',
		CASE DGParzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZCATEGORY || ''
		END AS 'DGParzPhotosHigh-Category',
		CASE DGParzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGParzPhotosHigh-Visibility State',
		CASE DGParzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGParzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGParzPhotosHigh-Enrichment State',
		DGParzPhotosHigh.ZENRICHMENTVERSION AS 'DGParzPhotosHigh-Enrichment Version',
		DGParzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGParzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGASSETS AS 'zAsset-Highlight Being Assets Key',
		HBAzPhotosHigh.ZUUID AS 'HBAzPhotosHigh-UUID',
		HBAzPhotosHigh.Z_PK AS 'HBAzPhotosHigh-zPK',
		HBAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBAzPhotosHigh-Parent PH Key',
		HBAzPhotosHigh.Z_ENT AS 'HBAzPhotosHigh-zENT',
		HBAzPhotosHigh.Z_OPT AS 'HBAzPhotosHigh-zOPT',
		HBAzPhotosHigh.ZPROMOTIONSCORE AS 'HBAzPhotosHigh-Promotion Score',
		HBAzPhotosHigh.ZTITLE AS 'HBAzPhotosHigh-Title',
		HBAzPhotosHigh.ZSUBTITLE AS 'HBAzPhotosHigh-Subtitle',
		HBAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBAzPhotosHigh-Verbose Smart Description',
		DateTime(HBAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBAzPhotosHigh-Start Date',
		HBAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBAzPhotosHigh Start-Timezone Offset',
		HBAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBAzPhotosHigh-End Timezone Offset',
		DateTime(HBAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBAzPhotosHigh-End Date',
		HBAzPhotosHigh.ZASSETSCOUNT AS 'HBAzPhotosHigh-Asset Count',
		HBAzPhotosHigh.ZSUMMARYCOUNT AS 'HBAzPhotosHigh-Summary Count',
		HBAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBAzPhotosHigh-Extended Count',
		HBAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBAzPhotosHigh-Day Group Assets Count',
		HBAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBAzPhotosHigh-Day Group Ext Assets Count',
		HBAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBAzPhotosHigh-Day Group Summary Assets Count',
		HBAzPhotosHigh.ZKEYASSET AS 'HBAzPhotosHigh-Key Asset',
		CASE HBAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZISCURATED || ''
		END AS 'HBAzPhotosHigh-Is Curated',
		CASE HBAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZTYPE || ''
		END AS 'HBAzPhotosHigh-Type',
		CASE HBAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZKIND || ''
		END AS 'HBAzPhotosHigh-Kind',
		CASE HBAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBAzPhotosHigh-Category',
		CASE HBAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBAzPhotosHigh-Visibility State',
		CASE HBAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZMOOD || ''
		END AS 'HBAzPhotosHigh-Mood',
		CASE HBAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBAzPhotosHigh-Enrichment State',
		HBAzPhotosHigh.ZENRICHMENTVERSION AS 'HBAzPhotosHigh-Enrichment Version',
		HBAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBAzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Highlight Being Extended Assets Key',
		HBEAzPhotosHigh.ZUUID AS 'HBEAzPhotosHigh-UUID',
		HBEAzPhotosHigh.Z_PK AS 'HBEAzPhotosHigh-zPK',
		HBEAzPhotosHigh.Z_ENT AS 'HBEAzPhotosHigh-zENT',
		HBEAzPhotosHigh.Z_OPT AS 'HBEAzPhotosHigh-zOPT',
		HBEAzPhotosHigh.ZPROMOTIONSCORE AS 'HBEAzPhotosHigh-Promotion Score',
		HBEAzPhotosHigh.ZTITLE AS 'HBEAzPhotosHigh-Title',
		HBEAzPhotosHigh.ZSUBTITLE AS 'HBEAzPhotosHigh-Subtitle',
		HBEAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBEAzPhotosHigh-Verbose Smart Description',
		DateTime(HBEAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBEAzPhotosHigh-Start Date',
		HBEAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBEAzPhotosHigh-Start Timezone Offset',
		HBEAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBEAzPhotosHigh-End Timezone Offset',
		DateTime(HBEAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBEAzPhotosHigh-End Date',
		HBEAzPhotosHigh.ZASSETSCOUNT AS 'HBEAzPhotosHigh-Asset Count',
		HBEAzPhotosHigh.ZSUMMARYCOUNT AS 'HBEAzPhotosHigh-Summary Count',
		HBEAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBEAzPhotosHigh-Extended Count',
		HBEAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBEAzPhotosHigh-Day Group Assets Count',
		HBEAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBEAzPhotosHigh-Day Group Ext Assets Count',
		HBEAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBEAzPhotosHigh-Day Group Summary Assets Count',
		HBEAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBEAzPhotosHigh-Parent PH Key',
		HBEAzPhotosHigh.ZYEARKEYASSET AS 'HBEAzPhotosHigh-Year Key Asset',
		HBEAzPhotosHigh.ZMONTHFIRSTASSET AS 'HBEAzPhotosHigh-Month First Asset',
		HBEAzPhotosHigh.ZMONTHKEYASSET AS 'HBEAzPhotosHigh-Month Key Asset',
		HBEAzPhotosHigh.ZKEYASSET AS 'HBEAzPhotosHigh-Key Asset',
		HBEAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'HBEAzPhotosHigh-Parent Day Group PH Key',
		HBEAzPhotosHigh.ZDAYGROUPKEYASSET AS 'HBEAzPhotosHigh-Day Group Key Asset',
		CASE HBEAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZISCURATED || ''
		END AS 'HBEAzPhotosHigh-is Curated',
		CASE HBEAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZTYPE || ''
		END AS 'HBEAzPhotosHigh-Type',
		CASE HBEAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZKIND || ''
		END AS 'HBEAzPhotosHigh-Kind',
		CASE HBEAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBEAzPhotosHigh-Category',
		CASE HBEAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBEAzPhotosHigh-Visibility State',
		CASE HBEAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZMOOD || ''
		END AS 'HBEAzPhotosHigh-Mood',
		CASE HBEAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBEAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBEAzPhotosHigh-Enrichment State',
		HBEAzPhotosHigh.ZENRICHMENTVERSION AS 'HBEAzPhotosHigh-Enrichment Version',
		HBEAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBEAzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Highlight Being Summary Assets Key',
		HBSAzPhotosHigh.ZUUID AS 'HBSAzPhotosHigh-UUID',
		HBSAzPhotosHigh.Z_PK AS 'HBSAzPhotosHigh-zPK',
		HBSAzPhotosHigh.Z_ENT AS 'HBSAzPhotosHigh-zENT',
		HBSAzPhotosHigh.Z_OPT AS 'HBSAzPhotosHigh-zOPT',
		HBSAzPhotosHigh.ZPROMOTIONSCORE AS 'HBSAzPhotosHigh-Promotion Score',
		HBSAzPhotosHigh.ZTITLE AS 'HBSAzPhotosHigh-Title',
		HBSAzPhotosHigh.ZSUBTITLE AS 'HBSAzPhotosHigh-Subtitle',
		HBSAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBSAzPhotosHigh-Verbose Smart Description',
		DateTime(HBSAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBSAzPhotosHigh-Start Date',
		HBSAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBSAzPhotosHigh-Start Timezone Offset',
		HBSAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBSAzPhotosHigh-End Timezone Offset',
		DateTime(HBSAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBSAzPhotosHigh-End Date',
		HBSAzPhotosHigh.ZASSETSCOUNT AS 'HBSAzPhotosHigh-Asset Count',
		HBSAzPhotosHigh.ZSUMMARYCOUNT AS 'HBSAzPhotosHigh-Summary Count',
		HBSAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBSAzPhotosHigh-Extended Count',
		HBSAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBSAzPhotosHigh-Day Group Assets Count',
		HBSAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBSAzPhotosHigh-Day Group Ext Assets Count',
		HBSAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBSAzPhotosHigh-Day Group Summary Assets Count',
		HBSAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBSAzPhotosHigh-Parent PH Key',
		HBSAzPhotosHigh.ZYEARKEYASSET AS 'HBSAzPhotosHigh-Year Key Asset',
		HBSAzPhotosHigh.ZMONTHFIRSTASSET AS 'HBSAzPhotosHigh-Month First Asset',
		HBSAzPhotosHigh.ZMONTHKEYASSET AS 'HBSAzPhotosHigh-Month Key Asset',
		HBSAzPhotosHigh.ZKEYASSET AS 'HBSAzPhotosHigh-Key Asset',
		HBSAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'HBSAzPhotosHigh-Parent Day Group PH Key',
		HBSAzPhotosHigh.ZDAYGROUPKEYASSET AS 'HBSAzPhotosHigh-Day Group Key Asset',
		CASE HBSAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZISCURATED || ''
		END AS 'HBSAzPhotosHigh-is Curated',
		CASE HBSAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZTYPE || ''
		END AS 'HBSAzPhotosHigh-Type',
		CASE HBSAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZKIND || ''
		END AS 'HBSAzPhotosHigh-Kind',
		CASE HBSAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBSAzPhotosHigh-Category',
		CASE HBSAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBSAzPhotosHigh-Visibility State',
		CASE HBSAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZMOOD || ''
		END AS 'HBSAzPhotosHigh-Mood',
		CASE HBSAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBSAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBSAzPhotosHigh-Enrichment State',
		HBSAzPhotosHigh.ZENRICHMENTVERSION AS 'HBSAzPhotosHigh-Enrichment Version',
		HBSAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBSAzPhotosHigh-Highlight Version',
		zAsset.ZHIGHLIGHTBEINGKEYASSET AS 'zAsset-Highlight Being Key Asset Key',
		HBKAzPhotosHigh.ZUUID AS 'HBKAzPhotosHigh-UUID',
		HBKAzPhotosHigh.Z_PK AS 'HBKAzPhotosHigh-zPK',
		HBKAzPhotosHigh.Z_ENT AS 'HBKAzPhotosHigh-zENT',
		HBKAzPhotosHigh.Z_OPT AS 'HBKAzPhotosHigh-zOPT',
		HBKAzPhotosHigh.ZPROMOTIONSCORE AS 'HBKAzPhotosHigh-Promotion Score',
		HBKAzPhotosHigh.ZTITLE AS 'HBKAzPhotosHigh-Title',
		HBKAzPhotosHigh.ZSUBTITLE AS 'HBKAzPhotosHigh-Subtitle',
		HBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'HBKAzPhotosHigh-Verbose Smart Description',
		DateTime(HBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'HBKAzPhotosHigh-Start Date',
		HBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'HBKAzPhotosHigh-Start Timezone Offset',
		HBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'HBKAzPhotosHigh-End Timezone Offset',
		DateTime(HBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'HBKAzPhotosHigh-End Date',
		HBKAzPhotosHigh.ZASSETSCOUNT AS 'HBKAzPhotosHigh-Asset Count',
		HBKAzPhotosHigh.ZSUMMARYCOUNT AS 'HBKAzPhotosHigh-Summary Count',
		HBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'HBKAzPhotosHigh-Extended Count',
		HBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'HBKAzPhotosHigh-Day Group Assets Count',
		HBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'HBKAzPhotosHigh-Day Group Ext Assets Count',
		HBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'HBKAzPhotosHigh-Day Group Summary Assets Count',
		HBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'HBKAzPhotosHigh-Parent PH Key',
		HBKAzPhotosHigh.ZYEARKEYASSET AS 'HBKAzPhotosHigh-Year Key Asset',
		HBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'HBKAzPhotosHigh-Month First Asset',
		HBKAzPhotosHigh.ZMONTHKEYASSET AS 'HBKAzPhotosHigh-Month Key Asset',
		HBKAzPhotosHigh.ZKEYASSET AS 'HBKAzPhotosHigh-Key Asset',
		HBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'HBKAzPhotosHigh-Parent Day Group PH Key',
		HBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'HBKAzPhotosHigh-Day Group Key Asset',
		CASE HBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZISCURATED || ''
		END AS 'HBKAzPhotosHigh-is Curated',
		CASE HBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZTYPE || ''
		END AS 'HBKAzPhotosHigh-Type',
		CASE HBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZKIND || ''
		END AS 'HBKAzPhotosHigh-Kind',
		CASE HBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'HBKAzPhotosHigh-Category',
		CASE HBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'HBKAzPhotosHigh-Visibility State',
		CASE HBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZMOOD || ''
		END AS 'HBKAzPhotosHigh-Mood',
		CASE HBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || HBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'HBKAzPhotosHigh-Enrichment State',
		HBKAzPhotosHigh.ZENRICHMENTVERSION AS 'HBKAzPhotosHigh-Enrichment Version',
		HBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'HBKAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS AS 'zAsset-Day Group Highlight Being Assets Key',
		DGHBAzPhotosHigh.ZUUID AS 'DGHBAzPhotosHigh-UUID',
		DGHBAzPhotosHigh.Z_PK AS 'DGHBAzPhotosHigh-zPK',
		DGHBAzPhotosHigh.Z_ENT AS 'DGHBAzPhotosHigh-zENT',
		DGHBAzPhotosHigh.Z_OPT AS 'DGHBAzPhotosHigh-zOPT',
		DGHBAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBAzPhotosHigh-Promotion Score',
		DGHBAzPhotosHigh.ZTITLE AS 'DGHBAzPhotosHigh-Title',
		DGHBAzPhotosHigh.ZSUBTITLE AS 'DGHBAzPhotosHigh-Subtitle',
		DGHBAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBAzPhotosHigh-Start Date',
		DGHBAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBAzPhotosHigh-Start Timezone Offset',
		DGHBAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBAzPhotosHigh-End Date',
		DGHBAzPhotosHigh.ZASSETSCOUNT AS 'DGHBAzPhotosHigh-Asset Count',
		DGHBAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBAzPhotosHigh-Summary Count',
		DGHBAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBAzPhotosHigh-Extended Count',
		DGHBAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBAzPhotosHigh-Day Group Assets Count',
		DGHBAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBAzPhotosHigh-Day Group Ext Assets Count',
		DGHBAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBAzPhotosHigh-Day Group Summary Assets Count',
		DGHBAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBAzPhotosHigh-Parent PH Key',
		DGHBAzPhotosHigh.ZYEARKEYASSET AS 'DGHBAzPhotosHigh-Year Key Asset',
		DGHBAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBAzPhotosHigh-Month First Asset',
		DGHBAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBAzPhotosHigh-Month Key Asset',
		DGHBAzPhotosHigh.ZKEYASSET AS 'DGHBAzPhotosHigh-Key Asset',
		DGHBAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBAzPhotosHigh-Parent Day Group PH Key',
		DGHBAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBAzPhotosHigh-Day Group Key Asset',
		CASE DGHBAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBAzPhotosHigh-is Curated',
		CASE DGHBAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBAzPhotosHigh-Type',
		CASE DGHBAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZKIND || ''
		END AS 'DGHBAzPhotosHigh-Kind',
		CASE DGHBAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBAzPhotosHigh-Category',
		CASE DGHBAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZVISIBILITYSTATE
		END AS 'DGHBAzPhotosHigh-Visibility State',
		CASE DGHBAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBAzPhotosHigh-Mood',
		CASE DGHBAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBAzPhotosHigh-Enrichment State',
		DGHBAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBAzPhotosHigh-Enrichment Version',
		DGHBAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Day Group Highlight Being Extended Assets Key',
		DGHBEAzPhotosHigh.ZUUID AS 'DGHBEAzPhotosHigh-UUID',
		DGHBEAzPhotosHigh.Z_PK AS 'DGHBEAzPhotosHigh-zPK',
		DGHBEAzPhotosHigh.Z_ENT AS 'DGHBEAzPhotosHigh-zENT',
		DGHBEAzPhotosHigh.Z_OPT AS 'DGHBEAzPhotosHigh-zOPT',
		DGHBEAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBEAzPhotosHigh-Promotion Score',
		DGHBEAzPhotosHigh.ZTITLE AS 'DGHBEAzPhotosHigh-Title',
		DGHBEAzPhotosHigh.ZSUBTITLE AS 'DGHBEAzPhotosHigh-Subtitle',
		DGHBEAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBEAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBEAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBEAzPhotosHigh-Start Date',
		DGHBEAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBEAzPhotosHigh-Start Timezone Offset',
		DGHBEAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBEAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBEAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBEAzPhotosHigh-End Date',
		DGHBEAzPhotosHigh.ZASSETSCOUNT AS 'DGHBEAzPhotosHigh-Asset Count',
		DGHBEAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBEAzPhotosHigh-Summary Count',
		DGHBEAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBEAzPhotosHigh-Extended Count',
		DGHBEAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBEAzPhotosHigh-Day Group Assets Count',
		DGHBEAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBEAzPhotosHigh-Day Group Ext Assets Count',
		DGHBEAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBEAzPhotosHigh-Day Group Summary Assets Count',
		DGHBEAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBEAzPhotosHigh-Parent PH Key',
		DGHBEAzPhotosHigh.ZYEARKEYASSET AS 'DGHBEAzPhotosHigh-Year Key Asset',
		DGHBEAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBEAzPhotosHigh-Month First Asset',
		DGHBEAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBEAzPhotosHigh-Month Key Asset',
		DGHBEAzPhotosHigh.ZKEYASSET AS 'DGHBEAzPhotosHigh-Key Asset',
		DGHBEAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBEAzPhotosHigh-Parent Day Group PH Key',
		DGHBEAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBEAzPhotosHigh-Day Group Key Asset',
		CASE DGHBEAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBEAzPhotosHigh-is Curated',
		CASE DGHBEAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBEAzPhotosHigh-Type',
		CASE DGHBEAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZKIND || ''
		END AS 'DGHBEAzPhotosHigh-Kind',
		CASE DGHBEAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBEAzPhotosHigh-Category',
		CASE DGHBEAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGHBEAzPhotosHigh-Visibility State',
		CASE DGHBEAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBEAzPhotosHigh-Mood',
		CASE DGHBEAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBEAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBEAzPhotosHigh-Enrichment State',
		DGHBEAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBEAzPhotosHigh-Enrichment Version',
		DGHBEAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBEAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSET AS 'zAsset-Day Group Highlight Being Key Asset',
		DGHBKAzPhotosHigh.ZUUID AS 'DGHBKAzPhotosHigh-UUID',
		DGHBKAzPhotosHigh.Z_PK AS 'DGHBKAzPhotosHigh-zPK',
		DGHBKAzPhotosHigh.Z_ENT AS 'DGHBKAzPhotosHigh-zENT',
		DGHBKAzPhotosHigh.Z_OPT AS 'DGHBKAzPhotosHigh-zOPT',
		DGHBKAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBKAzPhotosHigh-Promotion Score',
		DGHBKAzPhotosHigh.ZTITLE AS 'DGHBKAzPhotosHigh-Title',
		DGHBKAzPhotosHigh.ZSUBTITLE AS 'DGHBKAzPhotosHigh-Subtitle',
		DGHBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBKAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBKAzPhotosHigh-Start Date',
		DGHBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBKAzPhotosHigh-Start Timezone Offset',
		DGHBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBKAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBKAzPhotosHigh-End Date',
		DGHBKAzPhotosHigh.ZASSETSCOUNT AS 'DGHBKAzPhotosHigh-Asset Count',
		DGHBKAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBKAzPhotosHigh-Summary Count',
		DGHBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBKAzPhotosHigh-Extended Count',
		DGHBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBKAzPhotosHigh-Day Group Assets Count',
		DGHBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBKAzPhotosHigh-Day Group Ext Assets Count',
		DGHBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBKAzPhotosHigh-Day Group Summary Assets Count',
		DGHBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBKAzPhotosHigh-Parent PH Key',
		DGHBKAzPhotosHigh.ZYEARKEYASSET AS 'DGHBKAzPhotosHigh-Year Key Asset',
		DGHBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBKAzPhotosHigh-Month First Asset',
		DGHBKAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBKAzPhotosHigh-Month Key Asset',
		DGHBKAzPhotosHigh.ZKEYASSET AS 'DGHBKAzPhotosHigh-Key Asset',
		DGHBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBKAzPhotosHigh-Parent Day Group PH Key',
		DGHBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBKAzPhotosHigh-Day Group Key Asset',
		CASE DGHBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBKAzPhotosHigh-is Curated',
		CASE DGHBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBKAzPhotosHigh-Type',
		CASE DGHBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZKIND || ''
		END AS 'DGHBKAzPhotosHigh-Kind',
		CASE DGHBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBKAzPhotosHigh-Category',
		CASE DGHBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGHBKAzPhotosHigh-Visibility State',
		CASE DGHBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBKAzPhotosHigh-Mood',
		CASE DGHBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBKAzPhotosHigh-Enrichment State',
		DGHBKAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBKAzPhotosHigh-Enrichment Version',
		DGHBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBKAzPhotosHigh-Highlight Version',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Day Group Highlight Being Summary Assets Key',
		DGHBSAzPhotosHigh.ZUUID AS 'DGHBSAzPhotosHigh-UUID',
		DGHBSAzPhotosHigh.Z_PK AS 'DGHBSAzPhotosHigh-zPK',
		DGHBSAzPhotosHigh.Z_ENT AS 'DGHBSAzPhotosHigh-zENT',
		DGHBSAzPhotosHigh.Z_OPT AS 'DGHBSAzPhotosHigh-zOPT',
		DGHBSAzPhotosHigh.ZPROMOTIONSCORE AS 'DGHBSAzPhotosHigh-Promotion Score',
		DGHBSAzPhotosHigh.ZTITLE AS 'DGHBSAzPhotosHigh-Title',
		DGHBSAzPhotosHigh.ZSUBTITLE AS 'DGHBSAzPhotosHigh-Subtitle',
		DGHBSAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'DGHBSAzPhotosHigh-Verbose Smart Description',
		DateTime(DGHBSAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'DGHBSAzPhotosHigh-Start Date',
		DGHBSAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'DGHBSAzPhotosHigh-Start Timezone Offset',
		DGHBSAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'DGHBSAzPhotosHigh-End Timezone Offset',
		DateTime(DGHBSAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'DGHBSAzPhotosHigh-End Date',
		DGHBSAzPhotosHigh.ZASSETSCOUNT AS 'DGHBSAzPhotosHigh-Asset Count',
		DGHBSAzPhotosHigh.ZSUMMARYCOUNT AS 'DGHBSAzPhotosHigh-Summary Count',
		DGHBSAzPhotosHigh.ZEXTENDEDCOUNT AS 'DGHBSAzPhotosHigh-Extended Count',
		DGHBSAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'DGHBSAzPhotosHigh-Day Group Assets Count',
		DGHBSAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'DGHBSAzPhotosHigh-Day Group Ext Assets Count',
		DGHBSAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'DGHBSAzPhotosHigh-Day Group Summary Assets Count',
		DGHBSAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'DGHBSAzPhotosHigh-Parent PH Key',
		DGHBSAzPhotosHigh.ZYEARKEYASSET AS 'DGHBSAzPhotosHigh-Year Key Asset',
		DGHBSAzPhotosHigh.ZMONTHFIRSTASSET AS 'DGHBSAzPhotosHigh-Month First Asset',
		DGHBSAzPhotosHigh.ZMONTHKEYASSET AS 'DGHBSAzPhotosHigh-Month Key Asset',
		DGHBSAzPhotosHigh.ZKEYASSET AS 'DGHBSAzPhotosHigh-Key Asset',
		DGHBSAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'DGHBSAzPhotosHigh-Parent Day Group PH Key',
		DGHBSAzPhotosHigh.ZDAYGROUPKEYASSET AS 'DGHBSAzPhotosHigh-Day Group Key Asset',
		CASE DGHBSAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZISCURATED || ''
		END AS 'DGHBSAzPhotosHigh-is Curated',
		CASE DGHBSAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZTYPE || ''
		END AS 'DGHBSAzPhotosHigh-Type',
		CASE DGHBSAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZKIND || ''
		END AS 'DGHBSAzPhotosHigh-Kind',
		CASE DGHBSAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZCATEGORY || ''
		END AS 'DGHBSAzPhotosHigh-Category',
		CASE DGHBSAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'DGHBSAzPhotosHigh-Visibility State',
		CASE DGHBSAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZMOOD || ''
		END AS 'DGHBSAzPhotosHigh-Mood',
		CASE DGHBSAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || DGHBSAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'DGHBSAzPhotosHigh-Enrichment State',
		DGHBSAzPhotosHigh.ZENRICHMENTVERSION AS 'DGHBSAzPhotosHigh-Enrichment Version',
		DGHBSAzPhotosHigh.ZHIGHLIGHTVERSION AS 'DGHBSAzPhotosHigh-Highlight Version',
		zAsset.ZMONTHHIGHLIGHTBEINGFIRSTASSET AS 'zAsset-Month Highlight Being First Asset Key',
		MHBFAzPhotosHigh.ZUUID AS 'MHBFAzPhotosHigh-UUID',
		MHBFAzPhotosHigh.Z_PK AS 'MHBFAzPhotosHigh-zPK',
		MHBFAzPhotosHigh.Z_ENT AS 'MHBFAzPhotosHigh-zENT',
		MHBFAzPhotosHigh.Z_OPT AS 'MHBFAzPhotosHigh-zOPT',
		MHBFAzPhotosHigh.ZPROMOTIONSCORE AS 'MHBFAzPhotosHigh-Promotion Score',
		MHBFAzPhotosHigh.ZTITLE AS 'MHBFAzPhotosHigh-Title',
		MHBFAzPhotosHigh.ZSUBTITLE AS 'MHBFAzPhotosHigh-Subtitle',
		MHBFAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'MHBFAzPhotosHigh-Verbose Smart Description',
		DateTime(MHBFAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'MHBFAzPhotosHigh-Start Date',
		MHBFAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'MHBFAzPhotosHigh-Start Timezone Offset',
		MHBFAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'MHBFAzPhotosHigh-End Timezone Offset',
		DateTime(MHBFAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'MHBFAzPhotosHigh-End Date',
		MHBFAzPhotosHigh.ZASSETSCOUNT AS 'MHBFAzPhotosHigh-Asset Count',
		MHBFAzPhotosHigh.ZSUMMARYCOUNT AS 'MHBFAzPhotosHigh-Summary Count',
		MHBFAzPhotosHigh.ZEXTENDEDCOUNT AS 'MHBFAzPhotosHigh-Extended Count',
		MHBFAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'MHBFAzPhotosHigh-Day Group Assets Count',
		MHBFAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'MHBFAzPhotosHigh-Day Group Ext Assets Count',
		MHBFAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'MHBFAzPhotosHigh-Day Group Summary Assets Count',
		MHBFAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'MHBFAzPhotosHigh-Parent PH Key',
		MHBFAzPhotosHigh.ZYEARKEYASSET AS 'MHBFAzPhotosHigh-Year Key Asset',
		MHBFAzPhotosHigh.ZMONTHFIRSTASSET AS 'MHBFAzPhotosHigh-Month First Asset',
		MHBFAzPhotosHigh.ZMONTHKEYASSET AS 'MHBFAzPhotosHigh-Month Key Asset',
		MHBFAzPhotosHigh.ZKEYASSET AS 'MHBFAzPhotosHigh-Key Asset',
		MHBFAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'MHBFAzPhotosHigh-Parent Day Group PH Key',
		MHBFAzPhotosHigh.ZDAYGROUPKEYASSET AS 'MHBFAzPhotosHigh-Day Group Key Asset',
		CASE MHBFAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZISCURATED || ''
		END AS 'MHBFAzPhotosHigh-is Curated',
		CASE MHBFAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZTYPE || ''
		END AS 'MHBFAzPhotosHigh-Type',
		CASE MHBFAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZKIND || ''
		END AS 'MHBFAzPhotosHigh-Kind',
		CASE MHBFAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZCATEGORY || ''
		END AS 'MHBFAzPhotosHigh-Category',
		CASE MHBFAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'MHBFAzPhotosHigh-Visibility State',
		CASE MHBFAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZMOOD || ''
		END AS 'MHBFAzPhotosHigh-Mood',
		CASE MHBFAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBFAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'MHBFAzPhotosHigh-Enrichment State',
		MHBFAzPhotosHigh.ZENRICHMENTVERSION AS 'MHBFAzPhotosHigh-Enrichment Version',
		MHBFAzPhotosHigh.ZHIGHLIGHTVERSION AS 'MHBFAzPhotosHigh-Highlight Version',
		zAsset.ZMONTHHIGHLIGHTBEINGKEYASSET AS 'zAsset-Month Highlight Being Key Asset',
		MHBKAzPhotosHigh.ZUUID AS 'MHBKAzPhotosHigh-UUID',
		MHBKAzPhotosHigh.Z_PK AS 'MHBKAzPhotosHigh-zPK',
		MHBKAzPhotosHigh.Z_ENT AS 'MHBKAzPhotosHigh-zENT',
		MHBKAzPhotosHigh.Z_OPT AS 'MHBKAzPhotosHigh-zOPT',
		MHBKAzPhotosHigh.ZPROMOTIONSCORE AS 'MHBKAzPhotosHigh-Promotion Score',
		MHBKAzPhotosHigh.ZTITLE AS 'MHBKAzPhotosHigh-Title',
		MHBKAzPhotosHigh.ZSUBTITLE AS 'MHBKAzPhotosHigh-Subtitle',
		MHBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'MHBKAzPhotosHigh-Verbose Smart Description',
		DateTime(MHBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'MHBKAzPhotosHigh-Start Date',
		MHBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'MHBKAzPhotosHigh-Start Timezone Offset',
		MHBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'MHBKAzPhotosHigh-End Timezone Offset',
		DateTime(MHBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'MHBKAzPhotosHigh-End Date',
		MHBKAzPhotosHigh.ZASSETSCOUNT AS 'MHBKAzPhotosHigh-Asset Count',
		MHBKAzPhotosHigh.ZSUMMARYCOUNT AS 'MHBKAzPhotosHigh-Summary Count',
		MHBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'MHBKAzPhotosHigh-Extended Count',
		MHBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'MHBKAzPhotosHigh-Day Group Assets Count',
		MHBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'MHBKAzPhotosHigh-Day Group Ext Assets Count',
		MHBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'MHBKAzPhotosHigh-Day Group Summary Assets Count',
		MHBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'MHBKAzPhotosHigh-Parent PH Key',
		MHBKAzPhotosHigh.ZYEARKEYASSET AS 'MHBKAzPhotosHigh-Year Key Asset',
		MHBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'MHBKAzPhotosHigh-Month First Asset',
		MHBKAzPhotosHigh.ZMONTHKEYASSET AS 'MHBKAzPhotosHigh-Month Key Asset',
		MHBKAzPhotosHigh.ZKEYASSET AS 'MHBKAzPhotosHigh-Key Asset',
		MHBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'MHBKAzPhotosHigh-Parent Day Group PH Key',
		MHBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'MHBKAzPhotosHigh-Day Group Key Asset',
		CASE MHBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZISCURATED || ''
		END AS 'MHBKAzPhotosHigh-is Curated',
		CASE MHBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZTYPE || ''
		END AS 'MHBKAzPhotosHigh-Type',
		CASE MHBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZKIND || ''
		END AS 'MHBKAzPhotosHigh-Kind',
		CASE MHBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'MHBKAzPhotosHigh-Category',
		CASE MHBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'MHBKAzPhotosHigh-Visibility State',
		CASE MHBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZMOOD || ''
		END AS 'MHBKAzPhotosHigh-Mood',
		CASE MHBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || MHBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'MHBKAzPhotosHigh-Enrichment State',
		MHBKAzPhotosHigh.ZENRICHMENTVERSION AS 'MHBKAzPhotosHigh-Enrichment Version',
		MHBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'MHBKAzPhotosHigh-Highlight Version',
		zAsset.ZYEARHIGHLIGHTBEINGKEYASSET AS 'zAsset-Year Highlight Being Key Asset',
		YHBKAzPhotosHigh.ZUUID AS 'YHBKAzPhotosHigh-UUID',
		YHBKAzPhotosHigh.Z_PK AS 'YHBKAzPhotosHigh-zPK',
		YHBKAzPhotosHigh.Z_ENT AS 'YHBKAzPhotosHigh-zENT',
		YHBKAzPhotosHigh.Z_OPT AS 'YHBKAzPhotosHigh-zOPT',
		YHBKAzPhotosHigh.ZPROMOTIONSCORE AS 'YHBKAzPhotosHigh-Promotion Score',
		YHBKAzPhotosHigh.ZTITLE AS 'YHBKAzPhotosHigh-Title',
		YHBKAzPhotosHigh.ZSUBTITLE AS 'YHBKAzPhotosHigh-Subtitle',
		YHBKAzPhotosHigh.ZVERBOSESMARTDESCRIPTION AS 'YHBKAzPhotosHigh-Verbose Smart Description',
		DateTime(YHBKAzPhotosHigh.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'YHBKAzPhotosHigh-Start Date',
		YHBKAzPhotosHigh.ZSTARTTIMEZONEOFFSET AS 'YHBKAzPhotosHigh-Start Timezone Offset',
		YHBKAzPhotosHigh.ZENDTIMEZONEOFFSET AS 'YHBKAzPhotosHigh-End Timezone Offset',
		DateTime(YHBKAzPhotosHigh.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'YHBKAzPhotosHigh-End Date',
		YHBKAzPhotosHigh.ZASSETSCOUNT AS 'YHBKAzPhotosHigh-Asset Count',
		YHBKAzPhotosHigh.ZSUMMARYCOUNT AS 'YHBKAzPhotosHigh-Summary Count',
		YHBKAzPhotosHigh.ZEXTENDEDCOUNT AS 'YHBKAzPhotosHigh-Extended Count',
		YHBKAzPhotosHigh.ZDAYGROUPASSETSCOUNT AS 'YHBKAzPhotosHigh-Day Group Assets Count',
		YHBKAzPhotosHigh.ZDAYGROUPEXTENDEDASSETSCOUNT AS 'YHBKAzPhotosHigh-Day Group Ext Assets Count',
		YHBKAzPhotosHigh.ZDAYGROUPSUMMARYASSETSCOUNT AS 'YHBKAzPhotosHigh-Day Group Summary Assets Count',
		YHBKAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT AS 'YHBKAzPhotosHigh-Parent PH Key',
		YHBKAzPhotosHigh.ZYEARKEYASSET AS 'YHBKAzPhotosHigh-Year Key Asset',
		YHBKAzPhotosHigh.ZMONTHFIRSTASSET AS 'YHBKAzPhotosHigh-Month First Asset',
		YHBKAzPhotosHigh.ZMONTHKEYASSET AS 'YHBKAzPhotosHigh-Month Key Asset',
		YHBKAzPhotosHigh.ZKEYASSET AS 'YHBKAzPhotosHigh-Key Asset',
		YHBKAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT AS 'YHBKAzPhotosHigh-Parent Day Group PH Key',
		YHBKAzPhotosHigh.ZDAYGROUPKEYASSET AS 'YHBKAzPhotosHigh-Day Group Key Asset',
		CASE YHBKAzPhotosHigh.ZISCURATED
			WHEN 0 THEN '0-Not Curated'
			WHEN 1 THEN '1-Is Curated'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZISCURATED || ''
		END AS 'YHBKAzPhotosHigh-is Curated',
		CASE YHBKAzPhotosHigh.ZTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-Photos Highlights Day Group'
			WHEN 4 THEN '4-StillTesting'
			WHEN 5 THEN '5-StillTesting'
			WHEN 6 THEN '6-Parent Day Group Photos Highlight'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZTYPE || ''
		END AS 'YHBKAzPhotosHigh-Type',
		CASE YHBKAzPhotosHigh.ZKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Year&Month Photo Highlights-1'
			WHEN 2 THEN 'Year Photo Highlights-2'
			WHEN 3 THEN 'Day Group Assets Photo Highlights-3'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZKIND || ''
		END AS 'YHBKAzPhotosHigh-Kind',
		CASE YHBKAzPhotosHigh.ZCATEGORY
			WHEN 0 THEN '0-Past Highlights'
			WHEN 1 THEN '1-Todays Highlights'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZCATEGORY || ''
		END AS 'YHBKAzPhotosHigh-Category',
		CASE YHBKAzPhotosHigh.ZVISIBILITYSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-Year&Month No Asset Count'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZVISIBILITYSTATE || ''
		END AS 'YHBKAzPhotosHigh-Visibility State',
		CASE YHBKAzPhotosHigh.ZMOOD
			WHEN 0 THEN '0-None'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			WHEN 16 THEN '16-StillTesting'
			WHEN 32 THEN '32-StillTesting'
			WHEN 64 THEN '64-StillTesting'
			WHEN 128 THEN '128-StillTesting'
			WHEN 512 THEN '512-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZMOOD || ''
		END AS 'YHBKAzPhotosHigh-Mood',
		CASE YHBKAzPhotosHigh.ZENRICHMENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			WHEN 2 THEN '2-StillTesting'
			WHEN 3 THEN '3-StillTesting'
			WHEN 4 THEN '4-StillTesting'
			ELSE 'Unknown-New-Value!: ' || YHBKAzPhotosHigh.ZENRICHMENTSTATE || ''
		END AS 'YHBKAzPhotosHigh-Enrichment State',
		YHBKAzPhotosHigh.ZENRICHMENTVERSION AS 'YHBKAzPhotosHigh-Enrichment Version',
		YHBKAzPhotosHigh.ZHIGHLIGHTVERSION AS 'YHBKAzPhotosHigh-Highlight Version',
		z3SuggBKA.Z_3KEYASSETS AS 'z3SuggBKA-3KeyAssets = zAsset-zPK',
		z3SuggBKA.Z_55SUGGESTIONSBEINGKEYASSETS AS 'z3SuggBKA-55SuggBeingKeyAssets = zSugg-zPK',
		SBKAzSugg.Z_PK AS 'SBKAzSugg-zPK',
		SBKAzSugg.ZUUID AS 'SBKAzSugg-UUID',
		DateTime(SBKAzSugg.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Start Date',
		CASE SBKAzSugg.ZSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZSTATE || ''
		END AS 'SBKAzSugg-State',
		CASE SBKAzSugg.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZFEATUREDSTATE || ''
		END AS 'SBKAzSugg-Featured State',
		CASE SBKAzSugg.ZNOTIFICATIONSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZNOTIFICATIONSTATE || ''
		END AS 'SBKAzSugg-Notification State',
		DateTime(SBKAzSugg.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Creation Date',
		DateTime(SBKAzSugg.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-End Date',
		DateTime(SBKAzSugg.ZACTIVATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Activation Date',
		DateTime(SBKAzSugg.ZEXPUNGEDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Expunge Date',
		DateTime(SBKAzSugg.ZRELEVANTUNTILDATE + 978307200, 'UNIXEPOCH') AS 'SBKAzSugg-Relevant Until Date',
		SBKAzSugg.ZTITLE AS 'SBKAzSugg-Title',
		SBKAzSugg.ZSUBTITLE AS 'SBKAzSugg-Sub Title',
		SBKAzSugg.ZCACHEDCOUNT AS 'SBKAzSugg-Cached Count',
		SBKAzSugg.ZCACHEDPHOTOSCOUNT AS 'SBKAzSugg-Cahed Photos Count',
		SBKAzSugg.ZCACHEDVIDEOSCOUNT AS 'SBKAzSugg-Cached Videos Count',
		CASE SBKAzSugg.ZTYPE
			WHEN 5 THEN '5-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZTYPE || ''
		END AS 'SBKAzSugg-Type',
		CASE SBKAzSugg.ZSUBTYPE
			WHEN 501 THEN '501-StillTesting'
			WHEN 502 THEN '502-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZSUBTYPE || ''
		END AS 'SBKAzSugg-Sub Type',
		SBKAzSugg.ZVERSION AS 'SBKAzSugg-Version',
		CASE SBKAzSugg.ZCLOUDLOCALSTATE
			WHEN 0 THEN 'Suggestion Not Synced with Cloud-0'
			WHEN 1 THEN 'Suggestion Synced with Cloud-1'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZCLOUDLOCALSTATE || ''
		END AS 'SBKAzSugg-Cloud Local State',
		CASE SBKAzSugg.ZCLOUDDELETESTATE
			WHEN 0 THEN 'Suggestion Not Deleted-0'
			WHEN 1 THEN 'Suggestion Deleted-1'
			ELSE 'Unknown-New-Value!: ' || SBKAzSugg.ZCLOUDDELETESTATE || ''
		END AS 'SBKAzSugg-Cloud Delete State',
		z3SuggBRA.Z_3REPRESENTATIVEASSETS1 AS 'z3SuggBRA-3RepAssets1',
		z3SuggBRA.Z_55SUGGESTIONSBEINGREPRESENTATIVEASSETS AS 'z3SuggBRA-55SuggBeingRepAssets',
		SBRAzSugg.Z_PK AS 'SBRAzSugg-zPK',
		SBRAzSugg.ZUUID AS 'SBRAzSugg-UUID',
		DateTime(SBRAzSugg.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Start Date',
		CASE SBRAzSugg.ZSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZSTATE || ''
		END AS 'SBRAzSugg-State',
		CASE SBRAzSugg.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZFEATUREDSTATE || ''
		END AS 'SBRAzSugg-Featured State',
		CASE SBRAzSugg.ZNOTIFICATIONSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZNOTIFICATIONSTATE || ''
		END AS 'SBRAzSugg-Notification State',
		DateTime(SBRAzSugg.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Creation Date',
		DateTime(SBRAzSugg.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-End Date',
		DateTime(SBRAzSugg.ZACTIVATIONDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Activation Date',
		DateTime(SBRAzSugg.ZEXPUNGEDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Expunge Date',
		DateTime(SBRAzSugg.ZRELEVANTUNTILDATE + 978307200, 'UNIXEPOCH') AS 'SBRAzSugg-Relevant Until Date',
		SBRAzSugg.ZTITLE AS 'SBRAzSugg-Title',
		SBRAzSugg.ZSUBTITLE AS 'SBRAzSugg-Sub Title',
		SBRAzSugg.ZCACHEDCOUNT AS 'SBRAzSugg-Cached Count',
		SBRAzSugg.ZCACHEDPHOTOSCOUNT AS 'SBRAzSugg-Cahed Photos Count',
		SBRAzSugg.ZCACHEDVIDEOSCOUNT AS 'SBRAzSugg-Cached Videos Count',
		CASE SBRAzSugg.ZTYPE
			WHEN 5 THEN '5-StillTesting'
			ELSE 'StillTesting-New-Value!: ' || SBRAzSugg.ZTYPE || ''
		END AS 'SBRAzSugg-Type',
		CASE SBRAzSugg.ZSUBTYPE
			WHEN 501 THEN '501-StillTesting'
			WHEN 502 THEN '502-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZSUBTYPE || ''
		END AS 'SBRAzSugg-Sub Type',
		SBRAzSugg.ZVERSION AS 'SBRAzSugg-Version',
		CASE SBRAzSugg.ZCLOUDLOCALSTATE
			WHEN 0 THEN 'Suggestion Not Synced with Cloud-0'
			WHEN 1 THEN 'Suggestion Synced with Cloud-1'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZCLOUDLOCALSTATE || ''
		END AS 'SBRAzSugg-Cloud Local State',
		CASE SBRAzSugg.ZCLOUDDELETESTATE
			WHEN 0 THEN 'Suggestion Not Deleted-0'
			WHEN 1 THEN 'Suggestion Deleted-1'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZCLOUDDELETESTATE || ''
		END AS 'SBRAzSugg-Cloud Delete State',	
		zAsset.ZHIGHLIGHTVISIBILITYSCORE AS 'zAsset-Highlight Visibility Score',
		zMedAnlyAstAttr.ZMEDIAANALYSISVERSION AS 'zMedAnlyAstAttr-Media Analysis Version',
		zMedAnlyAstAttr.ZAUDIOCLASSIFICATION AS 'zMedAnlyAstAttr-Audio Classification',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Duration Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Start Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONVALUE AS 'zMedAnlyAstAttr-Best Video Range Duration Value',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTVALUE AS 'zMedAnlyAstAttr-Best Video Range Start Value',
		zMedAnlyAstAttr.ZPACKEDBESTPLAYBACKRECT AS 'zMedAnlyAstAttr-Packed Best Playback Rect',
		zMedAnlyAstAttr.ZACTIVITYSCORE AS 'zMedAnlyAstAttr-Activity Score',
		zMedAnlyAstAttr.ZVIDEOSCORE AS 'zMedAnlyAstAttr-Video Score',
		zMedAnlyAstAttr.ZAUTOPLAYSUGGESTIONSCORE AS 'zMedAnlyAstAttr-AutoPlay Suggestion Score',
		zMedAnlyAstAttr.ZBLURRINESSSCORE AS 'zMedAnlyAstAttr-Blurriness Score',
		zMedAnlyAstAttr.ZEXPOSURESCORE AS 'zMedAnlyAstAttr-Exposure Score',
		zAssetAnalyState.ZASSETUUID AS 'zAssetAnalyState-Asset UUID-4TableStart',
		zAssetAnalyState.ZANALYSISSTATE AS 'zAssetAnalyState-Analyisis State',
		zAssetAnalyState.ZWORKERFLAGS AS 'zAssetAnalyState-Worker Flags',
		zAssetAnalyState.ZWORKERTYPE AS 'zAssetAnalyState-Worker Type',
		DateTime(zAssetAnalyState.ZIGNOREUNTILDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Ignore Until Date',
		DateTime(zAssetAnalyState.ZLASTIGNOREDDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Last Ignored Date',
		DateTime(zAssetAnalyState.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Sort Token',
		zAsset.ZOVERALLAESTHETICSCORE AS 'zAsset-Overall Aesthetic Score',
		zCompAssetAttr.ZBEHAVIORALSCORE AS 'zCompAssetAttr-Behavioral Score',
		zCompAssetAttr.ZFAILURESCORE AS 'zCompAssetAttr-Failure Score zCompAssetAttr',
		zCompAssetAttr.ZHARMONIOUSCOLORSCORE AS 'zCompAssetAttr-Harmonious Color Score',
		zCompAssetAttr.ZIMMERSIVENESSSCORE AS 'zCompAssetAttr-Immersiveness Score',
		zCompAssetAttr.ZINTERACTIONSCORE AS 'zCompAssetAttr-Interaction Score',
		zCompAssetAttr.ZINTERESTINGSUBJECTSCORE AS 'zCompAssetAttr-Intersting Subject Score',
		zCompAssetAttr.ZINTRUSIVEOBJECTPRESENCESCORE AS 'zCompAssetAttr-Intrusive Object Presence Score',
		zCompAssetAttr.ZLIVELYCOLORSCORE AS 'zCompAssetAttr-Lively Color Score',
		zCompAssetAttr.ZLOWLIGHT AS 'zCompAssetAttr-Low Light',
		zCompAssetAttr.ZNOISESCORE AS 'zCompAssetAttr-Noise Score',
		zCompAssetAttr.ZPLEASANTCAMERATILTSCORE AS 'zCompAssetAttr-Pleasant Camera Tilt Score',
		zCompAssetAttr.ZPLEASANTCOMPOSITIONSCORE AS 'zCompAssetAttr-Pleasant Composition Score',
		zCompAssetAttr.ZPLEASANTLIGHTINGSCORE AS 'zCompAssetAttr-Pleasant Lighting Score',
		zCompAssetAttr.ZPLEASANTPATTERNSCORE AS 'zCompAssetAttr-Pleasant Pattern Score',
		zCompAssetAttr.ZPLEASANTPERSPECTIVESCORE AS 'zCompAssetAttr-Pleasant Perspective Score',
		zCompAssetAttr.ZPLEASANTPOSTPROCESSINGSCORE AS 'zCompAssetAttr-Pleasant Post Processing Score',
		zCompAssetAttr.ZPLEASANTREFLECTIONSSCORE AS 'zCompAssetAttr-Pleasant Reflection Score',
		zCompAssetAttr.ZPLEASANTSYMMETRYSCORE AS 'zCompAssetAttrPleasant Symmetry Score',
		zCompAssetAttr.ZSHARPLYFOCUSEDSUBJECTSCORE AS 'zCompAssetAttr-Sharply Focused Subject Score',
		zCompAssetAttr.ZTASTEFULLYBLURREDSCORE AS 'zCompAssetAttr-Tastfully Blurred Score',
		zCompAssetAttr.ZWELLCHOSENSUBJECTSCORE AS 'zCompAssetAttr-Well Chosen Subject Score',
		zCompAssetAttr.ZWELLFRAMEDSUBJECTSCORE AS 'zCompAssetAttr-Well Framed Subject Score',
		zCompAssetAttr.ZWELLTIMEDSHOTSCORE AS 'zCompAssetAttr-Well Timeed Shot Score',
		zCldRes.ZASSETUUID AS 'zCldRes-Asset UUID-4TableStart',
		zCldRes.ZCLOUDLOCALSTATE AS 'zCldRes-Cloud Local State',
		zCldRes.ZFILESIZE AS 'zCldRes-File Size',
		zCldRes.ZHEIGHT AS 'zCldRes-Height',
		zCldRes.ZISAVAILABLE AS 'zCldRes-Is Available',
		zCldRes.ZISLOCALLYAVAILABLE AS 'zCldRes-Is Locally Available',
		zCldRes.ZPREFETCHCOUNT AS 'zCldRes-Prefetch Count',
		zCldRes.ZSOURCETYPE AS 'zCldRes-Source Type',
		zCldRes.ZTYPE AS 'zCldRes-Type',
		zCldRes.ZWIDTH AS 'zCldRes-Width',
		zCldRes.ZDATECREATED AS 'zCldRes-Date Created',
		zCldRes.ZLASTONDEMANDDOWNLOADDATE AS 'zCldRes-Last OnDemand Download Date',
		zCldRes.ZLASTPREFETCHDATE AS 'zCldRes-Last Prefetch Date',
		zCldRes.ZPRUNEDAT AS 'zCldRes-Prunedat',
		zCldRes.ZFILEPATH AS 'zCldRes-File Path',
		zCldRes.ZFINGERPRINT AS 'zCldRes-Fingerprint',
		zCldRes.ZITEMIDENTIFIER AS 'zCldRes-Item ID',
		zCldRes.ZUNIFORMTYPEIDENTIFIER AS 'zCldRes-UniID',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAddAssetAttr.Z_ENT AS 'zAddAssetAttr-zENT',
		zAddAssetAttr.Z_OPT AS 'ZAddAssetAttr-zOPT',
		zAddAssetAttr.ZASSET AS 'zAddAssetAttr-zAsset= zAsset_zPK',
		zAddAssetAttr.ZUNMANAGEDADJUSTMENT AS 'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK',
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
		zAddAssetAttr.ZPUBLICGLOBALUUID AS 'zAddAssetAttr-Public Global UUID',
		zAddAssetAttr.ZDEFERREDPHOTOIDENTIFIER AS 'zAddAssetAttr-Deferred Photo Identifier',
		zAddAssetAttr.ZORIGINALASSETSUUID AS 'zAddAssetAttr-Original Assets UUID',
		zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
		zAddAssetAttr.ZORIGINATINGASSETIDENTIFIER AS 'zAddAssetAttr-Originating Asset Identifier',
		zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',
		zAlbumList.Z_PK AS 'zAlbumList-zPK= Album List Key',
		zAlbumList.Z_ENT AS 'zAlbumList-zENT',
		zAlbumList.Z_OPT AS 'zAlbumList-zOPT',
		zAlbumList.ZIDENTIFIER AS 'zAlbumList-ID Key',
		zAlbumList.ZUUID AS 'zAlbumList-UUID',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAsset.Z_ENT AS 'zAsset-zENT',
		zAsset.Z_OPT AS 'zAsset-zOPT',
		zAsset.ZMASTER AS 'zAsset-Master= zCldMast-zPK',
		zAsset.ZEXTENDEDATTRIBUTES AS 'zAsset-Extended Attributes= zExtAttr-zPK',
		zAsset.ZIMPORTSESSION AS 'zAsset-Import Session Key',
		zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZMOMENTSHARE AS 'zAsset-Moment Share Key= zShare-zPK',
		zAsset.ZMOMENT AS 'zAsset-zMoment Key= zMoment-zPK',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZHIGHLIGHTBEINGASSETS AS 'zAsset-Highlight Being Assets-HBA Key',
		zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Highlight Being Extended Assets-HBEA Key',
		zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Highligh Being Summary Assets-HBSA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS AS 'zAsset-Day Group Highlight Being Assets-DGHBA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key',
		zAsset.ZPROMOTIONSCORE AS 'zAsset-Promotion Score',
		zAsset.ZMEDIAANALYSISATTRIBUTES AS 'zAsset-Media Analysis Attributes Key',
		zAsset.ZMEDIAGROUPUUID AS 'zAsset-Media Group UUID',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAsset.ZCLOUDASSETGUID AS 'zAsset-Cloud_Asset_GUID = store.cloudphotodb',
		zAsset.ZCLOUDCOLLECTIONGUID AS 'zAsset.Cloud Collection GUID',
		zAsset.ZAVALANCHEUUID AS 'zAsset-Avalanche UUID',
		zAssetAnalyState.Z_PK AS 'zAssetAnalyState-zPK',
		zAssetAnalyState.Z_ENT AS 'zAssetAnalyState-zEnt',
		zAssetAnalyState.Z_OPT AS 'zAssetAnalyState-zOpt',
		zAssetAnalyState.ZASSET AS 'zAssetAnalyState-Asset= zAsset-zPK',
		zAssetAnalyState.ZASSETUUID AS 'zAssetAnalyState-Asset UUID',
		zAssetDes.Z_PK AS 'zAssetDes-zPK',
		zAssetDes.Z_ENT AS 'zAssetDes-zENT',
		zAssetDes.Z_OPT AS 'zAssetDes-zOPT',
		zAssetDes.ZASSETATTRIBUTES AS 'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK',
		zCldFeedEnt.Z_PK AS 'zCldFeedEnt-zPK= zCldShared keys',
		zCldFeedEnt.Z_ENT AS 'zCldFeedEnt-zENT',
		zCldFeedEnt.Z_OPT AS 'zCldFeedEnt-zOPT',
		zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID',
		zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID',
		zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID',
		zCldMast.Z_PK AS 'zCldMast-zPK= zAsset-Master',
		zCldMast.Z_ENT AS 'zCldMast-zENT',
		zCldMast.Z_OPT AS 'zCldMast-zOPT',
		zCldMast.ZMOMENTSHARE AS 'zCldMast-Moment Share Key= zShare-zPK',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		zCldMast.ZCLOUDMASTERGUID AS 'zCldMast-Cloud_Master_GUID = store.cloudphotodb',
		zCldMast.ZORIGINATINGASSETIDENTIFIER AS 'zCldMast-Originating Asset ID',
		zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CMzCldMastMedData.Z_ENT AS 'CMzCldMastMedData-zENT',
		CMzCldMastMedData.Z_OPT AS 'CMzCldMastMedData-zOPT',
		CMzCldMastMedData.ZCLOUDMASTER AS 'CMzCldMastMedData-CldMast= zCldMast-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		AAAzCldMastMedData.Z_ENT AS 'AAAzCldMastMedData-zENT',
		AAAzCldMastMedData.Z_OPT AS 'AAAzCldMastMedData-zOPT',
		AAAzCldMastMedData.ZCLOUDMASTER AS 'AAAzCldMastMedData-CldMast key',
		AAAzCldMastMedData.ZADDITIONALASSETATTRIBUTES AS 'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK',
		zCldRes.Z_PK AS 'zCldRes-zPK',
		zCldRes.Z_ENT AS 'zCldRes-zENT',
		zCldRes.Z_OPT AS 'zCldRes-zOPT',
		zCldRes.ZASSET AS 'zCldRes-Asset= zAsset-zPK',
		zCldRes.ZCLOUDMASTER AS 'zCldRes-Cloud Master= zCldMast-zPK',
		zCldRes.ZASSETUUID AS 'zCldRes-Asset UUID',
		zCldShareAlbumInvRec.Z_PK AS 'zCldShareAlbumInvRec-zPK',
		zCldShareAlbumInvRec.Z_ENT AS 'zCldShareAlbumInvRec-zEnt',
		zCldShareAlbumInvRec.Z_OPT AS 'zCldShareAlbumInvRec-zOpt',
		zCldShareAlbumInvRec.ZALBUM AS 'zCldShareAlbumInvRec-Album Key',
		zCldShareAlbumInvRec.Z_FOK_ALBUM AS 'zCldShareAlbumInvRec-FOK Album Key',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
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
		zCompAssetAttr.Z_PK AS 'zCompAssetAttr-zPK',
		zCompAssetAttr.Z_ENT AS 'zCompAssetAttr-zEnt',
		zCompAssetAttr.Z_OPT AS 'zCompAssetAttr-zOpt',
		zCompAssetAttr.ZASSET AS 'zCompAssetAttr-Asset Key',
		zDetFace.Z_PK AS 'zDetFace-zPK',
		zDetFace.Z_ENT AS 'zDetFace-zEnt',
		zDetFace.Z_OPT AS 'zDetFace.zOpt',
		zDetFace.ZASSET AS 'zDetFace-Asset= zAsset-zPK or Asset Containing Face',
		zDetFace.ZPERSON AS 'zDetFace-Person= zPerson-zPK',
		zDetFace.ZPERSONBEINGKEYFACE AS 'zDetFace-Person Being Key Face',
		zDetFace.ZFACEPRINT AS 'zDetFace-Face Print',
		zDetFace.ZFACEGROUPBEINGKEYFACE AS 'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK',
		zDetFace.ZFACEGROUP AS 'zDetFace-FaceGroup= zDetFaceGroup-zPK',
		zDetFace.ZUUID AS 'zDetFace-UUID',
		zDetFaceGroup.Z_PK AS 'zDetFaceGroup-zPK',
		zDetFaceGroup.Z_ENT AS 'zDetFaceGroup-zENT',
		zDetFaceGroup.Z_OPT AS 'zDetFaceGroup-zOPT',
		zDetFaceGroup.ZASSOCIATEDPERSON AS 'zDetFaceGroup-AssocPerson= zPerson-zPK',
		zDetFaceGroup.ZKEYFACE AS 'zDetFaceGroup-KeyFace= zDetFace-zPK',
		zDetFaceGroup.ZUUID AS 'zDetFaceGroup-UUID',
		zDetFacePrint.Z_PK AS 'zDetFacePrint-zPK',
		zDetFacePrint.Z_ENT AS 'zDetFacePrint-zEnt',
		zDetFacePrint.Z_OPT AS 'zDetFacePrint-zOpt',
		zDetFacePrint.ZFACE AS 'zDetFacePrint-Face Key',
		zExtAttr.Z_PK AS 'zExtAttr-zPK= zAsset-zExtendedAttributes',
		zExtAttr.Z_ENT AS 'zExtAttr-zENT',
		zExtAttr.Z_OPT AS 'zExtAttr-zOPT',
		zExtAttr.ZASSET AS 'zExtAttr-Asset Key',
		zFaceCrop.Z_PK AS 'zFaceCrop-zPK',
		zFaceCrop.Z_ENT AS 'zFaceCrop-zEnt',
		zFaceCrop.Z_OPT AS 'zFaceCrop-zOpt',
		zFaceCrop.ZASSET AS 'zFaceCrop-Asset Key',
		zFaceCrop.ZINVALIDMERGECANDIDATEPERSONUUID AS 'zFaceCrop-Invalid Merge Canidate Person UUID',
		zFaceCrop.ZPERSON AS 'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key',
		zFaceCrop.ZFACE AS 'zFaceCrop-Face Key',
		zFaceCrop.ZUUID AS 'zFaceCrop-UUID',
		zGenAlbum.Z_PK AS 'zGenAlbum-zPK=26AlbumLists= 26Albums',
		zGenAlbum.Z_ENT AS 'zGenAlbum-zENT',
		zGenAlbum.Z_OPT AS 'zGenAlbum-zOpt',
		zGenAlbum.ZKEYASSET AS 'zGenAlbum-Key Asset-Key zAsset-zPK',
		zGenAlbum.ZSECONDARYKEYASSET AS 'zGenAlbum-Secondary Key Asset',
		zGenAlbum.ZTERTIARYKEYASSET AS 'zGenAlbum-Tertiary Key Asset',
		zGenAlbum.ZCUSTOMKEYASSET AS 'zGenAlbum-Custom Key Asset',
		zGenAlbum.ZPARENTFOLDER AS 'zGenAlbum-Parent Folder Key= zGenAlbum-zPK',
		zGenAlbum.Z_FOK_PARENTFOLDER AS 'zGenAlbum-FOK Parent Folder',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud_GUID = store.cloudphotodb',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',
		zIntResou.Z_PK AS 'zIntResou-zPK',
		zIntResou.Z_ENT AS 'zIntResou-zENT',
		zIntResou.Z_OPT AS 'zIntResou-zOPT',
		zIntResou.ZASSET AS 'zIntResou-Asset= zAsset_zPK',
		zIntResou.ZFINGERPRINT AS 'zIntResou-Fingerprint',
		zIntResou.ZCLOUDDELETEASSETUUIDWITHRESOURCETYPE AS 'zIntResou-Cloud Delete Asset UUID With Resource Type',
		zMedAnlyAstAttr.Z_PK AS 'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata',
		zMedAnlyAstAttr.Z_ENT AS 'zMedAnlyAstAttr-zEnt',
		zMedAnlyAstAttr.Z_OPT AS 'zMedAnlyAstAttr-zOpt',
		zMedAnlyAstAttr.ZASSET AS 'zMedAnlyAstAttr-Asset= zAsset-zPK',
		zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
		zPerson.Z_ENT AS 'zPerson-zEnt',
		zPerson.Z_OPT AS 'zPerson-zOpt',
		zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
		zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
		zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
		zSceneP.Z_PK AS 'zSceneP-zPK',
		zSceneP.Z_ENT AS 'zSceneP-zENT',
		zSceneP.Z_OPT AS 'zSceneP-zOPT',
		zShare.Z_PK AS 'zShare-zPK',
		zShare.Z_ENT AS 'zShare-zENT',
		zShare.Z_OPT AS 'zShare-zOPT',
		zShare.ZUUID AS 'zShare-UUID',
		SPLzShare.ZUUID AS 'SPLzShare-UUID',
		zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID = store.cloudphotodb',
		zSharePartic.Z_PK AS 'zSharePartic-zPK',
		zSharePartic.Z_ENT AS 'zSharePartic-zENT',
		zSharePartic.Z_OPT AS 'zSharePartic-zOPT',
		zSharePartic.ZSHARE AS 'zSharePartic-Share Key= zShare-zPK',
		zSharePartic.ZUUID AS 'zSharePartic-UUID',
		zUnmAdj.Z_PK AS 'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key',
		zUnmAdj.Z_OPT AS 'zUnmAdj-zOPT',
		zUnmAdj.Z_ENT AS 'zUnmAdj-zENT',
		zUnmAdj.ZASSETATTRIBUTES AS 'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK',
		zUnmAdj.ZUUID AS 'zUnmAdj-UUID',
		zUnmAdj.ZOTHERADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Other Adjustments Fingerprint',
		zUnmAdj.ZSIMILARTOORIGINALADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Similar to Orig Adjustments Fingerprint',
		z25AlbumLists.Z_25ALBUMS AS 'z25AlbumList-25Albums= zGenAlbum-zPK',
		z25AlbumLists.Z_2ALBUMLISTS AS 'z25AlbumList-Album List Key',
		z25AlbumLists.Z_FOK_25ALBUMS AS 'z25AlbumList-FOK25Albums Key',
		z26Assets.Z_26ALBUMS AS 'z26Assets-26Albums= zGenAlbum-zPK',
		z26Assets.Z_3ASSETS AS 'z26Assets-3Asset Key= zAsset-zPK in the Album',
		z26Assets.Z_FOK_3ASSETS AS 'z26Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT
			LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
			LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
			LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
			LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
			LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
			LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
			LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDRESOURCE zCldRes ON zCldRes.ZCLOUDMASTER = zCldMast.Z_PK
			LEFT JOIN ZASSETANALYSISSTATE zAssetAnalyState ON zAssetAnalyState.ZASSET = zAsset.Z_PK
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
			LEFT JOIN ZCOMPUTEDASSETATTRIBUTES zCompAssetAttr ON zCompAssetAttr.Z_PK = zAsset.ZCOMPUTEDATTRIBUTES
			LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
			LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
			LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
			LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.ZSHARE = SPLzShare.Z_PK
			LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
			LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
			LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
			LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
			LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
			LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
			LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
			LEFT JOIN Z_3MEMORIESBEINGCURATEDASSETS z3MemoryBCAs ON zAsset.Z_PK = z3MemoryBCAs.Z_3CURATEDASSETS
			LEFT JOIN ZMEMORY zMemory ON z3MemoryBCAs.Z_40MEMORIESBEINGCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGEXTENDEDCURATEDASSETS z3MemoryBECAs ON zAsset.Z_PK = z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AND z3MemoryBECAs.Z_40MEMORIESBEINGEXTENDEDCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGMOVIECURATEDASSETS z3MemoryBMCAs ON zAsset.Z_PK = z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AND z3MemoryBMCAs.Z_40MEMORIESBEINGMOVIECURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGREPRESENTATIVEASSETS z3MemoryBRAs ON zAsset.Z_PK = z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AND z3MemoryBRAs.Z_40MEMORIESBEINGREPRESENTATIVEASSETS = zMemory.Z_PK
			LEFT JOIN ZMOMENT zMoment ON zMoment.Z_PK = zAsset.ZMOMENT
			LEFT JOIN ZMOMENTLIST YearzMomentList ON YearzMomentList.Z_PK = zMoment.ZYEARMOMENTLIST
			LEFT JOIN ZMOMENTLIST MegaYMzMomentList ON MegaYMzMomentList.Z_PK = zMoment.ZMEGAMOMENTLIST
			LEFT JOIN ZPHOTOSHIGHLIGHT HBAzPhotosHigh ON HBAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT HBEAzPhotosHigh ON HBEAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT HBKAzPhotosHigh ON HBKAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT HBSAzPhotosHigh ON HBSAzPhotosHigh.Z_PK = zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT YHBKAzPhotosHigh ON YHBKAzPhotosHigh.Z_PK = zAsset.ZYEARHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT MHBFAzPhotosHigh ON MHBFAzPhotosHigh.Z_PK = zAsset.ZMONTHHIGHLIGHTBEINGFIRSTASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT MHBKAzPhotosHigh ON MHBKAzPhotosHigh.Z_PK = zAsset.ZMONTHHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBAzPhotosHigh ON DGHBAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBEAzPhotosHigh ON DGHBEAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBKAzPhotosHigh ON DGHBKAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSET
			LEFT JOIN ZPHOTOSHIGHLIGHT DGHBSAzPhotosHigh ON DGHBSAzPhotosHigh.Z_PK = zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS
			LEFT JOIN ZPHOTOSHIGHLIGHT YMParzPhotosHigh ON YMParzPhotosHigh.Z_PK = HBAzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT
			LEFT JOIN ZPHOTOSHIGHLIGHT YearParzPhotosHigh ON YearParzPhotosHigh.Z_PK = YMParzPhotosHigh.ZPARENTPHOTOSHIGHLIGHT
			LEFT JOIN ZPHOTOSHIGHLIGHT DGParzPhotosHigh ON DGParzPhotosHigh.Z_PK = HBAzPhotosHigh.ZPARENTDAYGROUPPHOTOSHIGHLIGHT
			LEFT JOIN Z_3SUGGESTIONSBEINGKEYASSETS z3SuggBKA ON z3SuggBKA.Z_3KEYASSETS = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBKAzSugg ON SBKAzSugg.Z_PK = z3SuggBKA.Z_55SUGGESTIONSBEINGKEYASSETS
			LEFT JOIN Z_3SUGGESTIONSBEINGREPRESENTATIVEASSETS z3SuggBRA ON z3SuggBRA.Z_3REPRESENTATIVEASSETS1 = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBRAzSugg ON SBRAzSugg.Z_PK = z3SuggBRA.Z_55SUGGESTIONSBEINGREPRESENTATIVEASSETS
		ORDER BY zAsset.ZADDEDDATE
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
							row[268], row[269], row[270], row[271], row[272], row[273], row[274], row[275],
							row[276], row[277], row[278], row[279], row[280], row[281], row[282], row[283],
							row[284], row[285], row[286], row[287], row[288], row[289], row[290], row[291],
							row[292], row[293], row[294], row[295], row[296], row[297], row[298], row[299],
							row[300], row[301], row[302], row[303], row[304], row[305], row[306], row[307],
							row[308], row[309], row[310], row[311], row[312], row[313], row[314], row[315],
							row[316], row[317], row[318], row[319], row[320], row[321], row[322], row[323],
							row[324], row[325], row[326], row[327], row[328], row[329], row[330], row[331],
							row[332], row[333], row[334], row[335], row[336], row[337], row[338], row[339],
							row[340], row[341], row[342], row[343], row[344], row[345], row[346], row[347],
							row[348], row[349], row[350], row[351], row[352], row[353], row[354], row[355],
							row[356], row[357], row[358], row[359], row[360], row[361], row[362], row[363],
							row[364], row[365], row[366], row[367], row[368], row[369], row[370], row[371],
							row[372], row[373], row[374], row[375], row[376], row[377], row[378], row[379],
							row[380], row[381], row[382], row[383], row[384], row[385], row[386], row[387],
							row[388], row[389], row[390], row[391], row[392], row[393], row[394], row[395],
							row[396], row[397], row[398], row[399], row[400], row[401], row[402], row[403],
							row[404], row[405], row[406], row[407], row[408], row[409], row[410], row[411],
							row[412], row[413], row[414], row[415], row[416], row[417], row[418], row[419],
							row[420], row[421], row[422], row[423], row[424], row[425], row[426], row[427],
							row[428], row[429], row[430], row[431], row[432], row[433], row[434], row[435],
							row[436], row[437], row[438], row[439], row[440], row[441], row[442], row[443],
							row[444], row[445], row[446], row[447], row[448], row[449], row[450], row[451],
							row[452], row[453], row[454], row[455], row[456], row[457], row[458], row[459],
							row[460], row[461], row[462], row[463], row[464], row[465], row[466], row[467],
							row[468], row[469], row[470], row[471], row[472], row[473], row[474], row[475],
							row[476], row[477], row[478], row[479], row[480], row[481], row[482], row[483],
							row[484], row[485], row[486], row[487], row[488], row[489], row[490], row[491],
							row[492], row[493], row[494], row[495], row[496], row[497], row[498], row[499],
							row[500], row[501], row[502], row[503], row[504], row[505], row[506], row[507],
							row[508], row[509], row[510], row[511], row[512], row[513], row[514], row[515],
							row[516], row[517], row[518], row[519], row[520], row[521], row[522], row[523],
							row[524], row[525], row[526], row[527], row[528], row[529], row[530], row[531],
							row[532], row[533], row[534], row[535], row[536], row[537], row[538], row[539],
							row[540], row[541], row[542], row[543], row[544], row[545], row[546], row[547],
							row[548], row[549], row[550], row[551], row[552], row[553], row[554], row[555],
							row[556], row[557], row[558], row[559], row[560], row[561], row[562], row[563],
							row[564], row[565], row[566], row[567], row[568], row[569], row[570], row[571],
							row[572], row[573], row[574], row[575], row[576], row[577], row[578], row[579],
							row[580], row[581], row[582], row[583], row[584], row[585], row[586], row[587],
							row[588], row[589], row[590], row[591], row[592], row[593], row[594], row[595],
							row[596], row[597], row[598], row[599], row[600], row[601], row[602], row[603],
							row[604], row[605], row[606], row[607], row[608], row[609], row[610], row[611],
							row[612], row[613], row[614], row[615], row[616], row[617], row[618], row[619],
							row[620], row[621], row[622], row[623], row[624], row[625], row[626], row[627],
							row[628], row[629], row[630], row[631], row[632], row[633], row[634], row[635],
							row[636], row[637], row[638], row[639], row[640], row[641], row[642], row[643],
							row[644], row[645], row[646], row[647], row[648], row[649], row[650], row[651],
							row[652], row[653], row[654], row[655], row[656], row[657], row[658], row[659],
							row[660], row[661], row[662], row[663], row[664], row[665], row[666], row[667],
							row[668], row[669], row[670], row[671], row[672], row[673], row[674], row[675],
							row[676], row[677], row[678], row[679], row[680], row[681], row[682], row[683],
							row[684], row[685], row[686], row[687], row[688], row[689], row[690], row[691],
							row[692], row[693], row[694], row[695], row[696], row[697], row[698], row[699],
							row[700], row[701], row[702], row[703], row[704], row[705], row[706], row[707],
							row[708], row[709], row[710], row[711], row[712], row[713], row[714], row[715],
							row[716], row[717], row[718], row[719], row[720], row[721], row[722], row[723],
							row[724], row[725], row[726], row[727], row[728], row[729], row[730], row[731],
							row[732], row[733], row[734], row[735], row[736], row[737], row[738], row[739],
							row[740], row[741], row[742], row[743], row[744], row[745], row[746], row[747],
							row[748], row[749], row[750], row[751], row[752], row[753], row[754], row[755],
							row[756], row[757], row[758], row[759], row[760], row[761], row[762], row[763],
							row[764], row[765], row[766], row[767], row[768], row[769], row[770], row[771],
							row[772], row[773], row[774], row[775], row[776], row[777], row[778], row[779],
							row[780], row[781], row[782], row[783], row[784], row[785], row[786], row[787],
							row[788], row[789], row[790], row[791], row[792], row[793], row[794], row[795],
							row[796], row[797], row[798], row[799], row[800], row[801], row[802], row[803],
							row[804], row[805], row[806], row[807], row[808], row[809], row[810], row[811],
							row[812], row[813], row[814], row[815], row[816], row[817], row[818], row[819],
							row[820], row[821], row[822], row[823], row[824], row[825], row[826], row[827],
							row[828], row[829], row[830], row[831], row[832], row[833], row[834], row[835],
							row[836], row[837], row[838], row[839], row[840], row[841], row[842], row[843],
							row[844], row[845], row[846], row[847], row[848], row[849], row[850], row[851],
							row[852], row[853], row[854], row[855], row[856], row[857], row[858], row[859],
							row[860], row[861], row[862], row[863], row[864], row[865], row[866], row[867],
							row[868], row[869], row[870], row[871], row[872], row[873], row[874], row[875],
							row[876], row[877], row[878], row[879], row[880], row[881], row[882], row[883],
							row[884], row[885], row[886], row[887], row[888], row[889], row[890], row[891],
							row[892], row[893], row[894], row[895], row[896], row[897], row[898], row[899],
							row[900], row[901], row[902], row[903], row[904], row[905], row[906], row[907],
							row[908], row[909], row[910], row[911], row[912], row[913], row[914], row[915],
							row[916], row[917], row[918], row[919], row[920], row[921], row[922], row[923],
							row[924], row[925], row[926], row[927], row[928], row[929], row[930], row[931],
							row[932], row[933], row[934], row[935], row[936], row[937], row[938], row[939],
							row[940], row[941], row[942], row[943], row[944], row[945], row[946], row[947],
							row[948], row[949], row[950], row[951], row[952], row[953], row[954], row[955],
							row[956], row[957], row[958], row[959], row[960], row[961], row[962], row[963],
							row[964], row[965], row[966], row[967], row[968], row[969], row[970], row[971],
							row[972], row[973], row[974], row[975], row[976], row[977], row[978], row[979],
							row[980], row[981], row[982], row[983], row[984], row[985], row[986], row[987],
							row[988], row[989], row[990], row[991], row[992], row[993], row[994], row[995],
							row[996], row[997], row[998], row[999], row[1000], row[1001], row[1002],
							row[1003], row[1004], row[1005], row[1006], row[1007], row[1008], row[1009],
							row[1010], row[1011], row[1012], row[1013], row[1014], row[1015], row[1016],
							row[1017], row[1018], row[1019], row[1020], row[1021], row[1022], row[1023],
							row[1024], row[1025], row[1026], row[1027], row[1028], row[1029], row[1030],
							row[1031], row[1032], row[1033], row[1034], row[1035], row[1036], row[1037],
							row[1038], row[1039], row[1040], row[1041], row[1042], row[1043], row[1044],
							row[1045], row[1046], row[1047], row[1048], row[1049], row[1050], row[1051],
							row[1052], row[1053], row[1054], row[1055], row[1056], row[1057], row[1058],
							row[1059], row[1060], row[1061], row[1062], row[1063], row[1064], row[1065],
							row[1066], row[1067], row[1068], row[1069], row[1070], row[1071], row[1072],
							row[1073], row[1074], row[1075], row[1076], row[1077], row[1078], row[1079],
							row[1080], row[1081], row[1082], row[1083], row[1084], row[1085], row[1086],
							row[1087], row[1088], row[1089], row[1090], row[1091], row[1092], row[1093],
							row[1094], row[1095], row[1096], row[1097], row[1098], row[1099], row[1100],
							row[1101], row[1102], row[1103], row[1104], row[1105], row[1106], row[1107],
							row[1108], row[1109], row[1110], row[1111], row[1112], row[1113], row[1114],
							row[1115], row[1116], row[1117], row[1118], row[1119], row[1120], row[1121],
							row[1122], row[1123], row[1124], row[1125], row[1126], row[1127], row[1128],
							row[1129], row[1130], row[1131], row[1132], row[1133], row[1134], row[1135],
							row[1136], row[1137], row[1138], row[1139], row[1140], row[1141], row[1142],
							row[1143], row[1144], row[1145], row[1146], row[1147], row[1148], row[1149],
							row[1150], row[1151], row[1152], row[1153], row[1154], row[1155], row[1156],
							row[1157], row[1158], row[1159], row[1160], row[1161], row[1162], row[1163],
							row[1164], row[1165], row[1166], row[1167], row[1168], row[1169], row[1170],
							row[1171], row[1172], row[1173], row[1174], row[1175], row[1176], row[1177],
							row[1178], row[1179], row[1180], row[1181], row[1182], row[1183], row[1184],
							row[1185], row[1186], row[1187], row[1188], row[1189], row[1190], row[1191],
							row[1192], row[1193], row[1194], row[1195], row[1196], row[1197], row[1198],
							row[1199], row[1200], row[1201], row[1202], row[1203], row[1204], row[1205],
							row[1206], row[1207], row[1208], row[1209], row[1210], row[1211], row[1212],
							row[1213], row[1214], row[1215], row[1216], row[1217], row[1218], row[1219],
							row[1220], row[1221], row[1222], row[1223], row[1224], row[1225], row[1226],
							row[1227], row[1228], row[1229], row[1230], row[1231], row[1232], row[1233],
							row[1234], row[1235], row[1236], row[1237], row[1238], row[1239], row[1240],
							row[1241], row[1242], row[1243], row[1244], row[1245], row[1246], row[1247],
							row[1248], row[1249], row[1250], row[1251], row[1252], row[1253], row[1254],
							row[1255], row[1256], row[1257], row[1258], row[1259], row[1260], row[1261],
							row[1262], row[1263], row[1264], row[1265], row[1266], row[1267], row[1268],
							row[1269]))

		data_headers = (('zAsset-Added Date-0', 'datetime'),
						'zAsset- SortToken -CameraRoll-1',
						'zAsset Complete-2',
						'zAsset-zPK-4QueryStart-3',
						'zAddAssetAttr-zPK-4QueryStart-4',
						'zAsset-UUID = store.cloudphotodb-4QueryStart-5',
						'zAddAssetAttr-Master Fingerprint-4TableStart-6',
						'zIntResou-Fingerprint-4TableStart-7',
						'zAsset-Cloud is My Asset-8',
						'zAsset-Cloud is deletable-Asset-9',
						'zAsset-Cloud_Local_State-10',
						'zAsset-Visibility State-11',
						'zExtAttr-Camera Make-12',
						'zExtAttr-Camera Model-13',
						'zExtAttr-Lens Model-14',
						'zExtAttr-Flash Fired-15',
						'zExtAttr-Focal Lenght-16',
						'zAsset-Derived Camera Capture Device-17',
						'zAddAssetAttr-Camera Captured Device-18',
						'zAddAssetAttr-Imported by-19',
						'zCldMast-Imported By-20',
						'zAddAssetAttr-Creator Bundle ID-21',
						'zAddAssetAttr-Imported By Display Name-22',
						'zCldMast-Imported by Bundle ID-23',
						'zCldMast-Imported by Display Name-24',
						'zAsset-Saved Asset Type-25',
						'zAsset-Directory-Path-26',
						'zAsset-Filename-27',
						'zAddAssetAttr- Original Filename-28',
						'zCldMast- Original Filename-29',
						('zAsset-Date Created-30', 'datetime'),
						('zCldMast-Creation Date-31', 'datetime'),
						('zIntResou-CldMst Date Created-32', 'datetime'),
						'zAddAssetAttr-Time Zone Name-33',
						'zAddAssetAttr-Time Zone Offset-34',
						'zAddAssetAttr-Inferred Time Zone Offset-35',
						'zAddAssetAttr-EXIF-String-36',
						('zAsset-Modification Date-37', 'datetime'),
						('zAsset-Last Shared Date-38', 'datetime'),
						'zCldMast-Cloud Local State-39',
						('zCldMast-Import Date-40', 'datetime'),
						('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-41', 'datetime'),
						'zAddAssetAttr-Import Session ID-4QueryStart-42',
						('zAddAssetAttr-Alt Import Image Date-43', 'datetime'),
						'zCldMast-Import Session ID- AirDrop-StillTesting- 4QueryStart-44',
						('zAsset-Cloud Batch Publish Date-45', 'datetime'),
						('zAsset-Cloud Server Publish Date-46', 'datetime'),
						'zAsset-Cloud Download Requests-47',
						'zAsset-Cloud Batch ID-48',
						'zAddAssetAttr-Upload Attempts-49',
						'zAsset-Latitude-50',
						'zExtAttr-Latitude-51',
						'zAsset-Longitude-52',
						'zExtAttr-Longitude-53',
						'zAddAssetAttr-GPS Horizontal Accuracy-54',
						'zAddAssetAttr-Location Hash-55',
						'zAddAssetAttr-Shifted Location Valid-56',
						'zAddAssetAttr-Shifted Location Data-57',
						'zAddAssetAttr-Reverse Location Is Valid-58',
						'zAddAssetAttr-Reverse Location Data-59',
						'ParentzGenAlbum-UUID-4QueryStart-60',
						'zGenAlbum-UUID-4QueryStart-61',
						'ParentzGenAlbum-Cloud GUID-4QueryStart-62',
						'zGenAlbum-Cloud GUID-4QueryStart-63',
						'zCldShareAlbumInvRec-Album GUID-4QueryStart-64',
						'zCldShareAlbumInvRec-Cloud GUID-4QueryStart-65',
						'zGenAlbum-Project Render UUID-4QueryStart-66',
						'ParentzGenAlbum-Cloud-Local-State-4QueryStart-67',
						'zGenAlbum-Cloud_Local_State-4QueryStart-68',
						('ParentzGenAlbum- Creation Date- 4QueryStart-69', 'datetime'),
						('zGenAlbum- Creation Date- 4QueryStart-70', 'datetime'),
						('zGenAlbum- Cloud Creation Date- 4QueryStart-71', 'datetime'),
						('zGenAlbum- Start Date- 4QueryStart-72', 'datetime'),
						('zGenAlbum- End Date- 4QueryStart-73', 'datetime'),
						('zGenAlbum-Cloud Subscription Date- 4QueryStart-74', 'datetime'),
						'ParentzGenAlbum- Title- 4QueryStart-75',
						'zGenAlbum- Title-User&System Applied- 4QueryStart-76',
						'zGenAlbum-Import Session ID-SWY- 4QueryStart-77',
						'zGenAlbum-Creator Bundle ID- 4QueryStart-78',
						'zGenAlbum-zENT- Entity- 4QueryStart-79',
						'ParentzGenAlbum- Kind- 4QueryStart-80',
						'zGenAlbum-Album Kind- 4QueryStart-81',
						'AAAzCldMastMedData-zOPT-82',
						'zAddAssetAttr-Media Metadata Type-83',
						'AAAzCldMastMedData-Data-84',
						'CldMasterzCldMastMedData-zOPT-85',
						'zCldMast-Media Metadata Type-86',
						'CMzCldMastMedData-Data-87',
						'zAsset-Orientation-88',
						'zAddAssetAttr-Original Orientation-89',
						'zAsset-Kind-90',
						'zAsset-Kind-Sub-Type-91',
						'zAddAssetAttr-Cloud Kind Sub Type-92',
						'zAsset-Playback Style-93',
						'zAsset-Playback Variation-94',
						'zAsset-Video Duration-95',
						'zExtAttr-Duration-96',
						'zAsset-Video CP Duration-97',
						'zAddAssetAttr-Video CP Duration Time Scale-98',
						'zAsset-Video CP Visibility State-99',
						'zAddAssetAttr-Video CP Display Value-100',
						'zAddAssetAttr-Video CP Display Time Scale-101',
						'zIntResou-Datastore Class ID-102',
						'zAsset-Cloud Placeholder Kind-103',
						'zIntResou-Local Availability-104',
						'zIntResou-Local Availability Target-105',
						'zIntResou-Cloud Local State-106',
						'zIntResou-Remote Availability-107',
						'zIntResou-Remote Availability Target-108',
						'zIntResou-Transient Cloud Master-109',
						'zIntResou-Side Car Index-110',
						'zIntResou- File ID-111',
						'zIntResou-Version-112',
						'zAddAssetAttr- Original-File-Size-113',
						'zIntResou-Resource Type-114',
						'zIntResou-Datastore Sub-Type-115',
						'zIntResou-Cloud Source Type-116',
						'zIntResou-Data Length-117',
						'zIntResou-Recipe ID-118',
						('zIntResou-Cloud Last Prefetch Date-119', 'datetime'),
						'zIntResou-Cloud Prefetch Count-120',
						('zIntResou- Cloud-Last-OnDemand Download-Date-121', 'datetime'),
						'zAsset-Uniform Type ID-122',
						'zAsset-Original Color Space-123',
						'zCldMast-Uniform_Type_ID-124',
						'zCldMast-Full Size JPEG Source-125',
						'zAsset-HDR Gain-126',
						'zExtAttr-Codec-127',
						'zCldMast-Codec Name-128',
						'zCldMast-Video Frame Rate-129',
						'zCldMast-Placeholder State-130',
						'zAsset-Depth_Type-131',
						'zAsset-Avalanche UUID-4TableStart-132',
						'zAsset-Avalanche_Pick_Type-BurstAsset-133',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-134',
						'zAddAssetAttr-Cloud Recovery State-135',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-136',
						'zAsset-Deferred Processing Needed-137',
						'zAddAssetAttr-Deferred Photo Identifier-4QueryStart-138',
						'zAddAssetAttr-Deferred Processing Candidate Options-139',
						'zAsset-Has Adjustments-Camera-Effects-Filters-140',
						'zUnmAdj-UUID-4TableStart-141',
						'zAsset-Adjustment Timestamp-142',
						'zUnmAdj-Adjustment Timestamp-143',
						'zAddAssetAttr-Editor Bundle ID-144',
						'zUnmAdj-Editor Localized Name-145',
						'zUnmAdj-Adjustment Format ID-146',
						'zAddAssetAttr-Montage-147',
						'zUnmAdj-Adjustment Render Types-148',
						'zUnmAdj-Adjustment Format Version-149',
						'zUnmAdj-Adjustment Base Image Format-150',
						'zAsset-Favorite-151',
						'zAsset-Hidden-152',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-153',
						('zAsset-Trashed Date-154', 'datetime'),
						'zIntResou-Trash State-155',
						('zIntResou-Trashed Date-156', 'datetime'),
						'zAsset-Cloud Delete State-157',
						'zIntResou-Cloud Delete State-158',
						'zAddAssetAttr-PTP Trashed State-159',
						'zIntResou-PTP Trashed State-160',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-4TableStart-161',
						'zMedAnlyAstAttr-Media Analysis Timestamp-162',
						('zAsset-Analysis State Modificaion Date-163', 'datetime'),
						'zAddAssetAttr- Pending View Count-164',
						'zAddAssetAttr- View Count-165',
						'zAddAssetAttr- Pending Play Count-166',
						'zAddAssetAttr- Play Count-167',
						'zAddAssetAttr- Pending Share Count-168',
						'zAddAssetAttr- Share Count-169',
						'zAddAssetAttr-Allowed for Analysis-170',
						'zAddAssetAttr-Scene Analysis Version-171',
						'zAddAssetAttr-Scene Analysis Timestamp-172',
						'zAddAssetAttr-Destination Asset Copy State-173',
						'zAddAssetAttr-Variation Suggestions States-174',
						'zAsset-High Frame Rate State-175',
						'zAsset-Video Key Frame Time Scale-176',
						'zAsset-Video Key Frame Value-177',
						'zExtAttr-ISO-178',
						'zExtAttr-Metering Mode-179',
						'zExtAttr-Sample Rate-180',
						'zExtAttr-Track Format-181',
						'zExtAttr-White Balance-182',
						'zExtAttr-Aperture-183',
						'zExtAttr-BitRate-184',
						'zExtAttr-Exposure Bias-185',
						'zExtAttr-Frames Per Second-186',
						'zExtAttr-Shutter Speed-187',
						'zAsset-Height-188',
						'zAddAssetAttr-Original Height-189',
						'zIntResou-Unoriented Height-190',
						'zAsset-Width-191',
						'zAddAssetAttr-Original Width-192',
						'zIntResou-Unoriented Width-193',
						'zShare-Thumbnail Image Data-194',
						'SPLzShare-Thumbnail Image Data-195',
						'zAsset-Thumbnail Index-196',
						'zAddAssetAttr-Embedded Thumbnail Height-197',
						'zAddAssetAttr-Embedded Thumbnail Length-198',
						'zAddAssetAttr-Embedded Thumbnail Offset-199',
						'zAddAssetAttr-Embedded Thumbnail Width-200',
						'zAsset-Packed Acceptable Crop Rect-201',
						'zAsset-Packed Badge Attributes-202',
						'zAsset-Packed Preferred Crop Rect-203',
						'zAsset-Curation Score-204',
						'zAsset-Camera Processing Adjustment State-205',
						'zAsset-Depth Type-206',
						'zAddAssetAttr-Orig Resource Choice-207',
						'zAddAssetAttr-Spatial Over Capture Group ID-208',
						'zAddAssetAttr-Place Annotation Data-209',
						'zAddAssetAttr-Distance Identity-210',
						'zAddAssetAttr-Edited IPTC Attributes-211',
						'zAssetDes-Long Description-212',
						'zAddAssetAttr-Asset Description-213',
						'zAddAssetAttr-Title-Comments via Cloud Website-214',
						'zAddAssetAttr-Accessibility Description-215',
						'zAddAssetAttr-Photo Stream Tag ID-216',
						('zCldFeedEnt-Entry Date-217', 'datetime'),
						'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-218',
						'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-219',
						'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-220',
						'zCldFeedEnt-Entry Priority Number-221',
						'zCldFeedEnt-Entry Type Number-222',
						'zCldSharedComment-Cloud GUID-4TableStart-223',
						('zCldSharedComment-Date-224', 'datetime'),
						('zCldSharedComment-Comment Client Date-225', 'datetime'),
						('zAsset-Cloud Last Viewed Comment Date-226', 'datetime'),
						'zCldSharedComment-Type-227',
						'zCldSharedComment-Comment Text-228',
						'zCldSharedComment-Commenter Hashed Person ID-229',
						'zCldSharedComment-Batch Comment-230',
						'zCldSharedComment-Is a Caption-231',
						'zAsset-Cloud Has Comments by Me-232',
						'zCldSharedComment-Is My Comment-233',
						'zCldSharedComment-Is Deletable-234',
						'zAsset-Cloud Has Comments Conversation-235',
						'zAsset-Cloud Has Unseen Comments-236',
						'zCldSharedComment-Liked-237',
						'zAddAssetAttr-Share Type-238',
						'zShare-UUID-CMM-4TableStart-239',
						'SPLzShare-UUID-SPL-4TableStart-240',
						'zShare-zENT-CMM-241',
						'SPLzShare-zENT-SPL-242',
						'zShare-Status-CMM-243',
						'SPLzShare-Status-SPL-244',
						'zShare-Scope Type-CMM-245',
						'SPLzShare-Scope Type-SPL-246',
						'zShare-Local Publish State-CMM-247',
						'SPLzShare-Local Publish State-SPL-248',
						'zShare-Public Permission-CMM-249',
						'SPLzShare-Public Permission-SPL-250',
						'zShare-Originating Scope ID-CMM-251',
						'SPLzShare-Originating Scope ID-SPL-252',
						'zShare-Scope ID-CMM-253',
						'SPLzShare-Scope ID-SPL-254',
						'zShare-Title-CMM-255',
						'SPLzShare-Title-SPL-256',
						'zShare-Share URL-CMM-257',
						'SPLzShare-Share URL-SPL-258',
						('zShare-Creation Date-CMM-259', 'datetime'),
						('SPLzShare-Creation Date-SPL-260', 'datetime'),
						('zShare-Start Date-CMM-261', 'datetime'),
						('SPLzShare-Start Date-SPL-262', 'datetime'),
						('zShare-End Date-CMM-263', 'datetime'),
						('SPLzShare-End Date-SPL-264', 'datetime'),
						('zShare-Expiry Date-CMM-265', 'datetime'),
						('SPLzShare-Expiry Date-SPL-266', 'datetime'),
						'zShare-Asset Count-CMM-267',
						'SPLzShare-Asset Count-SPL-268',
						'zShare-Photos Count-CMM-269',
						'SPLzShare-Photos Count-CMM-SPL-270',
						'zShare-Uploaded Photos Count-CMM-271',
						'SPLzShare-Uploaded Photos Count-SPL-272',
						'zShare-Videos Count-CMM-273',
						'SPLzShare-Videos Count-SPL-274',
						'zShare-Uploaded Videos Count-CMM-275',
						'SPLzShare-Uploaded Videos Count-SPL-276',
						'zShare-Force Sync Attempted-CMM-277',
						'SPLzShare-Force Sync Attempted-SPL-278',
						'zShare-Should Notify On Upload Completion-CMM-279',
						'SPLzShare-Should Notify On Upload Completion-SPL-280',
						'zShare-Trashed State-CMM-281',
						'SPLzShare-Trashed State-SPL-282',
						'zShare-Cloud Delete State-CMM-283',
						'SPLzShare-Cloud Delete State-SPL-284',
						'zShare-Should Ignor Budgets-CMM-285',
						'SPLzShare-Should Ignor Budgets-SPL-286',
						'zSharePartic-UUID-4TableStart-287',
						'SPLzSharePartic-UUID-4TableStart-288',
						'zSharePartic-Acceptance Status-289',
						'SPLzSharePartic-Acceptance Status-290',
						'zSharePartic-Is Current User-291',
						'SPLzSharePartic-Is Current User-292',
						'zSharePartic-Role-293',
						'SPLzSharePartic-Role-294',
						'zSharePartic-Premission-295',
						'SPLzSharePartic-Premission-296',
						'zSharePartic-User ID-297',
						'SPLzSharePartic-User ID-298',
						'SPLzSharePartic-zPK-4TableStart-299',
						'zSharePartic-zPK-4TableStart-300',
						'zSharePartic-Email Address-301',
						'SPLzSharePartic-Email Address-302',
						'zSharePartic-Phone Number-303',
						'SPLzSharePartic-Phone Number-304',
						'ParentzGenAlbum-UUID-4TableStart-305',
						'zGenAlbum-UUID-4TableStart-306',
						'ParentzGenAlbum-Cloud GUID-4TableStart-307',
						'zGenAlbum-Cloud GUID-4TableStart-308',
						'zCldShareAlbumInvRec-Album GUID-4TableStart-309',
						'zCldShareAlbumInvRec-Cloud GUID-4TableStart-310',
						'zGenAlbum-Project Render UUID-4TableStart-311',
						'zAlbumList-Needs Reordering Number-312',
						'zGenAlbum-zENT- Entity-313',
						'ParentzGenAlbum-Kind-314',
						'zGenAlbum-Album Kind-315',
						'ParentzGenAlbum-Cloud-Local-State-316',
						'zGenAlbum-Cloud_Local_State-317',
						'ParentzGenAlbum- Title-318',
						'zGenAlbum- Title-User&System Applied-319',
						'zGenAlbum-Import Session ID-SWY-320',
						'zGenAlbum-Creator Bundle ID-321',
						('ParentzGenAlbum-Creation Date-322', 'datetime'),
						('zGenAlbum-Creation Date-323', 'datetime'),
						('zGenAlbum-Cloud Creation Date-324', 'datetime'),
						('zGenAlbum-Start Date-325', 'datetime'),
						('zGenAlbum-End Date-326', 'datetime'),
						('zGenAlbum-Cloud Subscription Date-327', 'datetime'),
						'ParentzGenAlbum-Pending Items Count-328',
						'zGenAlbum-Pending Items Count-329',
						'ParentzGenAlbum-Pending Items Type-330',
						'zGenAlbum-Pending Items Type-331',
						'zGenAlbum- Cached Photos Count-332',
						'zGenAlbum- Cached Videos Count-333',
						'zGenAlbum- Cached Count-334',
						'ParentzGenAlbum-Sync Event Order Key-335',
						'zGenAlbum-Sync Event Order Key-336',
						'zGenAlbum-Has Unseen Content-337',
						'zGenAlbum-Unseen Asset Count-338',
						'zGenAlbum-is Owned-339',
						'zGenAlbum-Cloud Relationship State-340',
						'zGenAlbum-Cloud Relationship State Local-341',
						'zGenAlbum-Cloud Owner Mail Key-342',
						'zGenAlbum-Cloud Owner Frist Name-343',
						'zGenAlbum-Cloud Owner Last Name-344',
						'zGenAlbum-Cloud Owner Full Name-345',
						'zGenAlbum-Cloud Person ID-346',
						'zAsset-Cloud Owner Hashed Person ID-347',
						'zGenAlbum-Cloud Owner Hashed Person ID-348',
						'zGenAlbum-Local Cloud Multi-Contributors Enabled-349',
						'zGenAlbum-Cloud Multi-Contributors Enabled-350',
						'zGenAlbum-Cloud Album Sub Type-351',
						('zGenAlbum-Cloud Contribution Date-352', 'datetime'),
						('zGenAlbum-Cloud Last Interesting Change Date-353', 'datetime'),
						'zGenAlbum-Cloud Notification Enabled-354',
						'ParentzGenAlbum-Pinned-355',
						'zGenAlbum-Pinned-356',
						'ParentzGenAlbum-Custom Sort Key-357',
						'zGenAlbum-Custom Sort Key-358',
						'ParentzGenAlbum-Custom Sort Ascending-359',
						'zGenAlbum-Custom Sort Ascending-360',
						'ParentzGenAlbum-Is Prototype-361',
						'zGenAlbum-Is Prototype-362',
						'ParentzGenAlbum-Project Document Type-363',
						'zGenAlbum-Project Document Type-364',
						'ParentzGenAlbum-Custom Query Type-365',
						'zGenAlbum-Custom Query Type-366',
						'ParentzGenAlbum-Trashed State-367',
						('ParentzGenAlbum-Trash Date-368', 'datetime'),
						'zGenAlbum-Trashed State-369',
						('zGenAlbum-Trash Date-370', 'datetime'),
						'ParentzGenAlbum-Cloud Delete State-371',
						'zGenAlbum-Cloud Delete State-372',
						'zGenAlbum-Cloud Owner Whitelisted-373',
						'zGenAlbum-Cloud Local Public URL Enabled-374',
						'zGenAlbum-Cloud Public URL Enabled-375',
						'zGenAlbum-Public URL-376',
						'zGenAlbum-Key Asset Face Thumb Index-377',
						'zGenAlbum-Project Text Extension ID-378',
						'zGenAlbum-User Query Data-379',
						'zGenAlbum-Custom Query Parameters-380',
						'zGenAlbum-Project Data-381',
						'zCldShareAlbumInvRec-Is My Invitation to Shared Album-382',
						'zCldShareAlbumInvRec-Invitation State Local-383',
						'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-384',
						('zCldShareAlbumInvRec-Subscription Date-385', 'datetime'),
						'zCldShareAlbumInvRec-Invitee First Name-386',
						'zCldShareAlbumInvRec-Invitee Last Name-387',
						'zCldShareAlbumInvRec-Invitee Full Name-388',
						'zCldShareAlbumInvRec-Invitee Hashed Person ID-389',
						'zCldShareAlbumInvRec-Invitee Email Key-390',
						'zGenAlbum-Key Asset Face ID-391',
						'zFaceCrop-Face Area Points-392',
						'zAsset-Face Adjustment Version-393',
						'zDetFace-Asset Visible-394',
						'zPerson-Face Count-395',
						'zDetFace-Face Crop-396',
						'zDetFace-Face Algorithm Version-397',
						'zDetFace-Adjustment Version-398',
						'zDetFace-UUID-4TableStart-399',
						'zPerson-Person UUID-4TableStart-400',
						'zDetFace-Confirmed Face Crop Generation State-401',
						'zDetFace-Manual-402',
						'zDetFace-VIP Model Type-403',
						'zDetFace-Name Source-404',
						'zDetFace-Cloud Name Source-405',
						'zPerson-Person URI-406',
						'zPerson-Display Name-407',
						'zPerson-Full Name-408',
						'zPerson-Cloud Verified Type-409',
						'zFaceCrop-State-410',
						'zFaceCrop-Type-411',
						'zFaceCrop-UUID-4TableStart-412',
						'zPerson-Type-413',
						'zPerson-Verified Type-414',
						'zPerson-Gender Type-415',
						'zDetFace-Gender Type-416',
						'zDetFace-Center X-417',
						'zDetFace-Center Y-418',
						'zPerson-Age Type Estimate-419',
						'zDetFace-Age Type Estimate-420',
						'zDetFace-Hair Color Type-421',
						'zDetFace-Facial Hair Type-422',
						'zDetFace-Has Smile-423',
						'zDetFace-Smile Type-424',
						'zDetFace-Lip Makeup Type-425',
						'zDetFace-Eyes State-426',
						'zDetFace-Is Left Eye Closed-427',
						'zDetFace-Is Right Eye Closed-428',
						'zDetFace-Eye Glasses Type-429',
						'zDetFace-Eye Makeup Type-430',
						'zDetFace-Cluster Squence Number Key-431',
						'zDetFace-Grouping ID-432',
						'zDetFace-Master ID-433',
						'zDetFace-Quality-434',
						'zDetFace-Quality Measure-435',
						'zDetFace-Source Height-436',
						'zDetFace-Source Width-437',
						'zDetFace-Hidden-Asset Hidden-438',
						'zDetFace-In Trash-Recently Deleted-439',
						'zDetFace-Cloud Local State-440',
						'zDetFace-Training Type-441',
						'zDetFace.Pose Yaw-442',
						'zDetFace-Roll-443',
						'zDetFace-Size-444',
						'zDetFace-Cluster Squence Number-445',
						'zDetFace-Blur Score-446',
						'zDetFacePrint-Face Print Version-447',
						'zMedAnlyAstAttr-Face Count-448',
						'zDetFaceGroup-UUID-4TableStart-449',
						'zDetFaceGroup-Person Builder State-450',
						'zDetFaceGroup-UnNamed Face Count-451',
						'zPerson-In Person Naming Model-452',
						'zPerson-Key Face Pick Source Key-453',
						'zPerson-Manual Order Key-454',
						'zPerson-Question Type-455',
						'zPerson-Suggested For Client Type-456',
						'zPerson-Merge Target Person-457',
						'zPerson-Cloud Local State-458',
						'zFaceCrop-Cloud Local State-459',
						'zFaceCrop-Cloud Type-460',
						'zPerson-Cloud Delete State-461',
						'zFaceCrop-Cloud Delete State-462',
						'zFaceCrop-Invalid Merge Canidate Person UUID-4TableStart-463',
						'zMemory-zPK-464',
						'z3MemoryBCAs-3CuratedAssets = zAsset-zPK-465',
						'z3MemoryBCAs-40MemoriesBeingCuratedAssets = zMemory-zPK-466',
						'z3MemoryBECAs-3ExtCuratedAssets = zAsset-zPK-467',
						'z3MemoryBECAs-40MemoriesBeingExtCuratedAssets = zMemory-zPK-468',
						'z3MemoryBMCAs-3MovieCuratedAssets = zAsset-zPK-469',
						'z3MemoryBMCAs-40MemoriesBeingMovieCuratedAssets = zMemory-zPK-470',
						'z3MemoryBRAs-3RepresentativeAssets = zAsset-zPK-471',
						'z3MemoryBRAs-40RepresentativeAssets = zMemory-zPK-472',
						'zMemory-Key Asset = zAsset-zPK-473',
						'zMemory-UUID-474',
						'zMemory-SubTitle-475',
						'zMemory-Title-476',
						'zMemory-Category-477',
						'zMemory-SubCategory-478',
						('zMemory-Creation Date-479', 'datetime'),
						'zMemory-User Created-480',
						'zMemory-Favorite Memory-481',
						'zMemory-Score-482',
						'zMemory-View Count-483',
						'zMemory-Play Count-484',
						'zMemory-Rejected-485',
						'zMemory-Share Count-486',
						('zMemory-Last Movie Play Date-487', 'datetime'),
						('zMemory-Last Viewed Date-488', 'datetime'),
						'zMemory-Pending-489',
						'zMemory-Pending Play Count Memory-490',
						'zMemory-Pending Share Count Memory-491',
						'zMemory-Pending View Count Memory-492',
						'zMemory-Featured State-493',
						'zMemory-Photos Graph Version-494',
						'zMemory-AssetListPredicte-495',
						'zMemory-Notification State-496',
						'zMemory-Cloud Local State-497',
						'zMemory-Cloud Delete State-498',
						'YearzMomentList-UUID-499',
						'YearzMomentList-zPK-500',
						'zMoment-Year Moment List-501',
						'YearzMomentList-Sort Index-502',
						'YearzMomentList-Granularity Level-503',
						('YearzMomentList-Start Date-504', 'datetime'),
						('YearzMomentList-Representative Date-505', 'datetime'),
						('YearzMomentList-End Date-506', 'datetime'),
						'YearzMomentList-Trashed State-507',
						'MegaYMzMomentList-UUID-508',
						'MegaYMzMomentList-zPK-509',
						'zMoment-Mega Moment List-510',
						'MegaYMzMomentList-Sort Index-511',
						'MegaYMzMomentList-Granularity Level-512',
						('MegaYMzMomentList-Start Date-513', 'datetime'),
						('MegaYMzMomentList-Representative Date-514', 'datetime'),
						('MegaYMzMomentList-End Date-515', 'datetime'),
						'MegaYMzMomentList-Trashed State-516',
						'zMoment-UUID-517',
						'zMoment-zPK-518',
						'zMoment-Aggregation Score-519',
						('zMoment-Start Date-520', 'datetime'),
						('zMoment-Representative Date-521', 'datetime'),
						'zMoment-Timezone Offset-522',
						('zMoment-Modification Date-523', 'datetime'),
						('zMoment-End Date-524', 'datetime'),
						'zMoment-SubTitle-525',
						'zMoment-Title-526',
						'zMoment-Processed Location-527',
						'zMoment-Approx Latitude-528',
						'zMoment-Approx Longitude-529',
						'zMoment-GPS Horizontal Accuracy-530',
						'zMoment-Cache Count-531',
						'zMoment-Cached Photos Count-532',
						'zMoment-Cached Videos Count-533',
						'zMoment-Trashed State-534',
						'zMoment-Highlight Key-535',
						'zAsset-Highlight Visibility Score-536',
						'YearParzPhotosHigh-UUID-537',
						'YearParzPhotosHigh-zPK-538',
						'YearParzPhotosHigh-zENT-539',
						'YearParzPhotosHigh-zOPT-540',
						'YearParzPhotosHigh-Promotion Score-541',
						'YearParzPhotosHigh-Title-542',
						'YearParzPhotosHigh-Verbose Smart Description-543',
						('YearParzPhotosHigh-Start Date-544', 'datetime'),
						('YearParzPhotosHigh-End Date-545', 'datetime'),
						'YearParzPhotosHigh-Year Key Asset-546',
						'YearParzPhotosHigh-Is Curated-547',
						'YearParzPhotosHigh-Kind-548',
						'YearParzPhotosHigh-Category-549',
						'YearParzPhotosHigh-Visibility State-550',
						'YearParzPhotosHigh-Enrichment State-551',
						'YearParzPhotosHigh-Enrichment Version-552',
						'YearParzPhotosHigh-Highlight Version-553',
						'YMParzPhotosHigh-UUID-554',
						'YMParzPhotosHigh-zPK-555',
						'YMParzPhotosHigh-Parent PH Key-556',
						'YMParzPhotosHigh-zENT-557',
						'YMParzPhotosHigh-zOPT-558',
						'YMParzPhotosHigh-Promotion Score-559',
						'YMParzPhotosHigh-Title-560',
						'YMParzPhotosHigh-Subtitle-561',
						'YMParzPhotosHigh-Verbose Smart Description-562',
						('YMParzPhotosHigh-Start Date-563', 'datetime'),
						('YMParzPhotosHigh-End Date-564', 'datetime'),
						'YMParzPhotosHigh-Month First Asset-565',
						'YMParzPhotosHigh-Month Key Asset-566',
						'YMParzPhotosHigh-Is Curated-567',
						'YMParzPhotosHigh-Kind-568',
						'YMParzPhotosHigh-Category-569',
						'YMParzPhotosHigh-Visibility State-570',
						'YMParzPhotosHigh-Enrichment State-571',
						'YMParzPhotosHigh-Enrichment Version-572',
						'YMParzPhotosHigh-Highlight Version-573',
						'DGParzPhotosHigh-UUID-574',
						'DGParzPhotosHigh-zPK-575',
						'DGParzPhotosHigh-Parent PH Key-576',
						'DGParzPhotosHigh-zENT-577',
						'DGParzPhotosHigh-zOPT-578',
						'DGParzPhotosHigh-Promotion Score-579',
						'DGParzPhotosHigh-Title-580',
						'DGParzPhotosHigh-Subtitle-581',
						'DGParzPhotosHigh-Verbose Smart Description-582',
						('DGParzPhotosHigh-Start Date-583', 'datetime'),
						('DGParzPhotosHigh-End Date-584', 'datetime'),
						'DGParzPhotosHigh-Month First Asset-585',
						'DGParzPhotosHigh-Month Key Asset-586',
						'DGParzPhotosHigh-Is Curated-587',
						'DGParzPhotosHigh-Kind-588',
						'DGParzPhotosHigh-Category-589',
						'DGParzPhotosHigh-Visibility State-590',
						'DGParzPhotosHigh-Enrichment State-591',
						'DGParzPhotosHigh-Enrichment Version-592',
						'DGParzPhotosHigh-Highlight Version-593',
						'zAsset-Highlight Being Assets Key-594',
						'HBAzPhotosHigh-UUID-595',
						'HBAzPhotosHigh-zPK-596',
						'HBAzPhotosHigh-Parent PH Key-597',
						'HBAzPhotosHigh-zENT-598',
						'HBAzPhotosHigh-zOPT-599',
						'HBAzPhotosHigh-Promotion Score-600',
						'HBAzPhotosHigh-Title-601',
						'HBAzPhotosHigh-Subtitle-602',
						'HBAzPhotosHigh-Verbose Smart Description-603',
						('HBAzPhotosHigh-Start Date-604', 'datetime'),
						'HBAzPhotosHigh Start-Timezone Offset-605',
						'HBAzPhotosHigh-End Timezone Offset-606',
						('HBAzPhotosHigh-End Date-607', 'datetime'),
						'HBAzPhotosHigh-Asset Count-608',
						'HBAzPhotosHigh-Summary Count-609',
						'HBAzPhotosHigh-Extended Count-610',
						'HBAzPhotosHigh-Day Group Assets Count-611',
						'HBAzPhotosHigh-Day Group Ext Assets Count-612',
						'HBAzPhotosHigh-Day Group Summary Assets Count-613',
						'HBAzPhotosHigh-Key Asset-614',
						'HBAzPhotosHigh-Is Curated-615',
						'HBAzPhotosHigh-Type-616',
						'HBAzPhotosHigh-Kind-617',
						'HBAzPhotosHigh-Category-618',
						'HBAzPhotosHigh-Visibility State-619',
						'HBAzPhotosHigh-Mood-620',
						'HBAzPhotosHigh-Enrichment State-621',
						'HBAzPhotosHigh-Enrichment Version-622',
						'HBAzPhotosHigh-Highlight Version-623',
						'zAsset-Highlight Being Extended Assets Key-624',
						'HBEAzPhotosHigh-UUID-625',
						'HBEAzPhotosHigh-zPK-626',
						'HBEAzPhotosHigh-zENT-627',
						'HBEAzPhotosHigh-zOPT-628',
						'HBEAzPhotosHigh-Promotion Score-629',
						'HBEAzPhotosHigh-Title-630',
						'HBEAzPhotosHigh-Subtitle-631',
						'HBEAzPhotosHigh-Verbose Smart Description-632',
						('HBEAzPhotosHigh-Start Date-633', 'datetime'),
						'HBEAzPhotosHigh-Start Timezone Offset-634',
						'HBEAzPhotosHigh-End Timezone Offset-635',
						('HBEAzPhotosHigh-End Date-636', 'datetime'),
						'HBEAzPhotosHigh-Asset Count-637',
						'HBEAzPhotosHigh-Summary Count-638',
						'HBEAzPhotosHigh-Extended Count-639',
						'HBEAzPhotosHigh-Day Group Assets Count-640',
						'HBEAzPhotosHigh-Day Group Ext Assets Count-641',
						'HBEAzPhotosHigh-Day Group Summary Assets Count-642',
						'HBEAzPhotosHigh-Parent PH Key-643',
						'HBEAzPhotosHigh-Year Key Asset-644',
						'HBEAzPhotosHigh-Month First Asset-645',
						'HBEAzPhotosHigh-Month Key Asset-646',
						'HBEAzPhotosHigh-Key Asset-647',
						'HBEAzPhotosHigh-Parent Day Group PH Key-648',
						'HBEAzPhotosHigh-Day Group Key Asset-649',
						'HBEAzPhotosHigh-is Curated-650',
						'HBEAzPhotosHigh-Type-651',
						'HBEAzPhotosHigh-Kind-652',
						'HBEAzPhotosHigh-Category-653',
						'HBEAzPhotosHigh-Visibility State-654',
						'HBEAzPhotosHigh-Mood-655',
						'HBEAzPhotosHigh-Enrichment State-656',
						'HBEAzPhotosHigh-Enrichment Version-657',
						'HBEAzPhotosHigh-Highlight Version-658',
						'zAsset-Highlight Being Summary Assets Key-659',
						'HBSAzPhotosHigh-UUID-660',
						'HBSAzPhotosHigh-zPK-661',
						'HBSAzPhotosHigh-zENT-662',
						'HBSAzPhotosHigh-zOPT-663',
						'HBSAzPhotosHigh-Promotion Score-664',
						'HBSAzPhotosHigh-Title-665',
						'HBSAzPhotosHigh-Subtitle-666',
						'HBSAzPhotosHigh-Verbose Smart Description-667',
						('HBSAzPhotosHigh-Start Date-668', 'datetime'),
						'HBSAzPhotosHigh-Start Timezone Offset-669',
						'HBSAzPhotosHigh-End Timezone Offset-670',
						('HBSAzPhotosHigh-End Date-671', 'datetime'),
						'HBSAzPhotosHigh-Asset Count-672',
						'HBSAzPhotosHigh-Summary Count-673',
						'HBSAzPhotosHigh-Extended Count-674',
						'HBSAzPhotosHigh-Day Group Assets Count-675',
						'HBSAzPhotosHigh-Day Group Ext Assets Count-676',
						'HBSAzPhotosHigh-Day Group Summary Assets Count-677',
						'HBSAzPhotosHigh-Parent PH Key-678',
						'HBSAzPhotosHigh-Year Key Asset-679',
						'HBSAzPhotosHigh-Month First Asset-680',
						'HBSAzPhotosHigh-Month Key Asset-681',
						'HBSAzPhotosHigh-Key Asset-682',
						'HBSAzPhotosHigh-Parent Day Group PH Key-683',
						'HBSAzPhotosHigh-Day Group Key Asset-684',
						'HBSAzPhotosHigh-is Curated-685',
						'HBSAzPhotosHigh-Type-686',
						'HBSAzPhotosHigh-Kind-687',
						'HBSAzPhotosHigh-Category-688',
						'HBSAzPhotosHigh-Visibility State-689',
						'HBSAzPhotosHigh-Mood-690',
						'HBSAzPhotosHigh-Enrichment State-691',
						'HBSAzPhotosHigh-Enrichment Version-692',
						'HBSAzPhotosHigh-Highlight Version-693',
						'zAsset-Highlight Being Key Asset Key-694',
						'HBKAzPhotosHigh-UUID-695',
						'HBKAzPhotosHigh-zPK-696',
						'HBKAzPhotosHigh-zENT-697',
						'HBKAzPhotosHigh-zOPT-698',
						'HBKAzPhotosHigh-Promotion Score-699',
						'HBKAzPhotosHigh-Title-700',
						'HBKAzPhotosHigh-Subtitle-701',
						'HBKAzPhotosHigh-Verbose Smart Description-702',
						('HBKAzPhotosHigh-Start Date-703', 'datetime'),
						'HBKAzPhotosHigh-Start Timezone Offset-704',
						'HBKAzPhotosHigh-End Timezone Offset-705',
						('HBKAzPhotosHigh-End Date-706', 'datetime'),
						'HBKAzPhotosHigh-Asset Count-707',
						'HBKAzPhotosHigh-Summary Count-708',
						'HBKAzPhotosHigh-Extended Count-709',
						'HBKAzPhotosHigh-Day Group Assets Count-710',
						'HBKAzPhotosHigh-Day Group Ext Assets Count-711',
						'HBKAzPhotosHigh-Day Group Summary Assets Count-712',
						'HBKAzPhotosHigh-Parent PH Key-713',
						'HBKAzPhotosHigh-Year Key Asset-714',
						'HBKAzPhotosHigh-Month First Asset-715',
						'HBKAzPhotosHigh-Month Key Asset-716',
						'HBKAzPhotosHigh-Key Asset-717',
						'HBKAzPhotosHigh-Parent Day Group PH Key-718',
						'HBKAzPhotosHigh-Day Group Key Asset-719',
						'HBKAzPhotosHigh-is Curated-720',
						'HBKAzPhotosHigh-Type-721',
						'HBKAzPhotosHigh-Kind-722',
						'HBKAzPhotosHigh-Category-723',
						'HBKAzPhotosHigh-Visibility State-724',
						'HBKAzPhotosHigh-Mood-725',
						'HBKAzPhotosHigh-Enrichment State-726',
						'HBKAzPhotosHigh-Enrichment Version-727',
						'HBKAzPhotosHigh-Highlight Version-728',
						'zAsset-Day Group Highlight Being Assets Key-729',
						'DGHBAzPhotosHigh-UUID-730',
						'DGHBAzPhotosHigh-zPK-731',
						'DGHBAzPhotosHigh-zENT-732',
						'DGHBAzPhotosHigh-zOPT-733',
						'DGHBAzPhotosHigh-Promotion Score-734',
						'DGHBAzPhotosHigh-Title-735',
						'DGHBAzPhotosHigh-Subtitle-736',
						'DGHBAzPhotosHigh-Verbose Smart Description-737',
						('DGHBAzPhotosHigh-Start Date-738', 'datetime'),
						'DGHBAzPhotosHigh-Start Timezone Offset-739',
						'DGHBAzPhotosHigh-End Timezone Offset-740',
						('DGHBAzPhotosHigh-End Date-741', 'datetime'),
						'DGHBAzPhotosHigh-Asset Count-742',
						'DGHBAzPhotosHigh-Summary Count-743',
						'DGHBAzPhotosHigh-Extended Count-744',
						'DGHBAzPhotosHigh-Day Group Assets Count-745',
						'DGHBAzPhotosHigh-Day Group Ext Assets Count-746',
						'DGHBAzPhotosHigh-Day Group Summary Assets Count-747',
						'DGHBAzPhotosHigh-Parent PH Key-748',
						'DGHBAzPhotosHigh-Year Key Asset-749',
						'DGHBAzPhotosHigh-Month First Asset-750',
						'DGHBAzPhotosHigh-Month Key Asset-751',
						'DGHBAzPhotosHigh-Key Asset-752',
						'DGHBAzPhotosHigh-Parent Day Group PH Key-753',
						'DGHBAzPhotosHigh-Day Group Key Asset-754',
						'DGHBAzPhotosHigh-is Curated-755',
						'DGHBAzPhotosHigh-Type-756',
						'DGHBAzPhotosHigh-Kind-757',
						'DGHBAzPhotosHigh-Category-758',
						'DGHBAzPhotosHigh-Visibility State-759',
						'DGHBAzPhotosHigh-Mood-760',
						'DGHBAzPhotosHigh-Enrichment State-761',
						'DGHBAzPhotosHigh-Enrichment Version-762',
						'DGHBAzPhotosHigh-Highlight Version-763',
						'zAsset-Day Group Highlight Being Extended Assets Key-764',
						'DGHBEAzPhotosHigh-UUID-765',
						'DGHBEAzPhotosHigh-zPK-766',
						'DGHBEAzPhotosHigh-zENT-767',
						'DGHBEAzPhotosHigh-zOPT-768',
						'DGHBEAzPhotosHigh-Promotion Score-769',
						'DGHBEAzPhotosHigh-Title-770',
						'DGHBEAzPhotosHigh-Subtitle-771',
						'DGHBEAzPhotosHigh-Verbose Smart Description-772',
						('DGHBEAzPhotosHigh-Start Date-773', 'datetime'),
						'DGHBEAzPhotosHigh-Start Timezone Offset-774',
						'DGHBEAzPhotosHigh-End Timezone Offset-775',
						('DGHBEAzPhotosHigh-End Date-776', 'datetime'),
						'DGHBEAzPhotosHigh-Asset Count-777',
						'DGHBEAzPhotosHigh-Summary Count-778',
						'DGHBEAzPhotosHigh-Extended Count-779',
						'DGHBEAzPhotosHigh-Day Group Assets Count-780',
						'DGHBEAzPhotosHigh-Day Group Ext Assets Count-781',
						'DGHBEAzPhotosHigh-Day Group Summary Assets Count-782',
						'DGHBEAzPhotosHigh-Parent PH Key-783',
						'DGHBEAzPhotosHigh-Year Key Asset-784',
						'DGHBEAzPhotosHigh-Month First Asset-785',
						'DGHBEAzPhotosHigh-Month Key Asset-786',
						'DGHBEAzPhotosHigh-Key Asset-787',
						'DGHBEAzPhotosHigh-Parent Day Group PH Key-788',
						'DGHBEAzPhotosHigh-Day Group Key Asset-789',
						'DGHBEAzPhotosHigh-is Curated-790',
						'DGHBEAzPhotosHigh-Type-791',
						'DGHBEAzPhotosHigh-Kind-792',
						'DGHBEAzPhotosHigh-Category-793',
						'DGHBEAzPhotosHigh-Visibility State-794',
						'DGHBEAzPhotosHigh-Mood-795',
						'DGHBEAzPhotosHigh-Enrichment State-796',
						'DGHBEAzPhotosHigh-Enrichment Version-797',
						'DGHBEAzPhotosHigh-Highlight Version-798',
						'zAsset-Day Group Highlight Being Key Asset-799',
						'DGHBKAzPhotosHigh-UUID-800',
						'DGHBKAzPhotosHigh-zPK-801',
						'DGHBKAzPhotosHigh-zENT-802',
						'DGHBKAzPhotosHigh-zOPT-803',
						'DGHBKAzPhotosHigh-Promotion Score-804',
						'DGHBKAzPhotosHigh-Title-805',
						'DGHBKAzPhotosHigh-Subtitle-806',
						'DGHBKAzPhotosHigh-Verbose Smart Description-807',
						('DGHBKAzPhotosHigh-Start Date-808', 'datetime'),
						'DGHBKAzPhotosHigh-Start Timezone Offset-809',
						'DGHBKAzPhotosHigh-End Timezone Offset-810',
						('DGHBKAzPhotosHigh-End Date-811', 'datetime'),
						'DGHBKAzPhotosHigh-Asset Count-812',
						'DGHBKAzPhotosHigh-Summary Count-813',
						'DGHBKAzPhotosHigh-Extended Count-814',
						'DGHBKAzPhotosHigh-Day Group Assets Count-815',
						'DGHBKAzPhotosHigh-Day Group Ext Assets Count-816',
						'DGHBKAzPhotosHigh-Day Group Summary Assets Count-817',
						'DGHBKAzPhotosHigh-Parent PH Key-818',
						'DGHBKAzPhotosHigh-Year Key Asset-819',
						'DGHBKAzPhotosHigh-Month First Asset-820',
						'DGHBKAzPhotosHigh-Month Key Asset-821',
						'DGHBKAzPhotosHigh-Key Asset-822',
						'DGHBKAzPhotosHigh-Parent Day Group PH Key-823',
						'DGHBKAzPhotosHigh-Day Group Key Asset-824',
						'DGHBKAzPhotosHigh-is Curated-825',
						'DGHBKAzPhotosHigh-Type-826',
						'DGHBKAzPhotosHigh-Kind-827',
						'DGHBKAzPhotosHigh-Category-828',
						'DGHBKAzPhotosHigh-Visibility State-829',
						'DGHBKAzPhotosHigh-Mood-830',
						'DGHBKAzPhotosHigh-Enrichment State-831',
						'DGHBKAzPhotosHigh-Enrichment Version-832',
						'DGHBKAzPhotosHigh-Highlight Version-833',
						'zAsset-Day Group Highlight Being Summary Assets Key-834',
						'DGHBSAzPhotosHigh-UUID-835',
						'DGHBSAzPhotosHigh-zPK-836',
						'DGHBSAzPhotosHigh-zENT-837',
						'DGHBSAzPhotosHigh-zOPT-838',
						'DGHBSAzPhotosHigh-Promotion Score-839',
						'DGHBSAzPhotosHigh-Title-840',
						'DGHBSAzPhotosHigh-Subtitle-841',
						'DGHBSAzPhotosHigh-Verbose Smart Description-842',
						('DGHBSAzPhotosHigh-Start Date-843', 'datetime'),
						'DGHBSAzPhotosHigh-Start Timezone Offset-844',
						'DGHBSAzPhotosHigh-End Timezone Offset-845',
						('DGHBSAzPhotosHigh-End Date-846', 'datetime'),
						'DGHBSAzPhotosHigh-Asset Count-847',
						'DGHBSAzPhotosHigh-Summary Count-848',
						'DGHBSAzPhotosHigh-Extended Count-849',
						'DGHBSAzPhotosHigh-Day Group Assets Count-850',
						'DGHBSAzPhotosHigh-Day Group Ext Assets Count-851',
						'DGHBSAzPhotosHigh-Day Group Summary Assets Count-852',
						'DGHBSAzPhotosHigh-Parent PH Key-853',
						'DGHBSAzPhotosHigh-Year Key Asset-854',
						'DGHBSAzPhotosHigh-Month First Asset-855',
						'DGHBSAzPhotosHigh-Month Key Asset-856',
						'DGHBSAzPhotosHigh-Key Asset-857',
						'DGHBSAzPhotosHigh-Parent Day Group PH Key-858',
						'DGHBSAzPhotosHigh-Day Group Key Asset-859',
						'DGHBSAzPhotosHigh-is Curated-860',
						'DGHBSAzPhotosHigh-Type-861',
						'DGHBSAzPhotosHigh-Kind-862',
						'DGHBSAzPhotosHigh-Category-863',
						'DGHBSAzPhotosHigh-Visibility State-864',
						'DGHBSAzPhotosHigh-Mood-865',
						'DGHBSAzPhotosHigh-Enrichment State-866',
						'DGHBSAzPhotosHigh-Enrichment Version-867',
						'DGHBSAzPhotosHigh-Highlight Version-868',
						'zAsset-Month Highlight Being First Asset Key-869',
						'MHBFAzPhotosHigh-UUID-870',
						'MHBFAzPhotosHigh-zPK-871',
						'MHBFAzPhotosHigh-zENT-872',
						'MHBFAzPhotosHigh-zOPT-873',
						'MHBFAzPhotosHigh-Promotion Score-874',
						'MHBFAzPhotosHigh-Title-875',
						'MHBFAzPhotosHigh-Subtitle-876',
						'MHBFAzPhotosHigh-Verbose Smart Description-877',
						('MHBFAzPhotosHigh-Start Date-878', 'datetime'),
						'MHBFAzPhotosHigh-Start Timezone Offset-879',
						'MHBFAzPhotosHigh-End Timezone Offset-880',
						('MHBFAzPhotosHigh-End Date-881', 'datetime'),
						'MHBFAzPhotosHigh-Asset Count-882',
						'MHBFAzPhotosHigh-Summary Count-883',
						'MHBFAzPhotosHigh-Extended Count-884',
						'MHBFAzPhotosHigh-Day Group Assets Count-885',
						'MHBFAzPhotosHigh-Day Group Ext Assets Count-886',
						'MHBFAzPhotosHigh-Day Group Summary Assets Count-887',
						'MHBFAzPhotosHigh-Parent PH Key-888',
						'MHBFAzPhotosHigh-Year Key Asset-889',
						'MHBFAzPhotosHigh-Month First Asset-890',
						'MHBFAzPhotosHigh-Month Key Asset-891',
						'MHBFAzPhotosHigh-Key Asset-892',
						'MHBFAzPhotosHigh-Parent Day Group PH Key-893',
						'MHBFAzPhotosHigh-Day Group Key Asset-894',
						'MHBFAzPhotosHigh-is Curated-895',
						'MHBFAzPhotosHigh-Type-896',
						'MHBFAzPhotosHigh-Kind-897',
						'MHBFAzPhotosHigh-Category-898',
						'MHBFAzPhotosHigh-Visibility State-899',
						'MHBFAzPhotosHigh-Mood-900',
						'MHBFAzPhotosHigh-Enrichment State-901',
						'MHBFAzPhotosHigh-Enrichment Version-902',
						'MHBFAzPhotosHigh-Highlight Version-903',
						'zAsset-Month Highlight Being Key Asset-904',
						'MHBKAzPhotosHigh-UUID-905',
						'MHBKAzPhotosHigh-zPK-906',
						'MHBKAzPhotosHigh-zENT-907',
						'MHBKAzPhotosHigh-zOPT-908',
						'MHBKAzPhotosHigh-Promotion Score-909',
						'MHBKAzPhotosHigh-Title-910',
						'MHBKAzPhotosHigh-Subtitle-911',
						'MHBKAzPhotosHigh-Verbose Smart Description-912',
						('MHBKAzPhotosHigh-Start Date-913', 'datetime'),
						'MHBKAzPhotosHigh-Start Timezone Offset-914',
						'MHBKAzPhotosHigh-End Timezone Offset-915',
						('MHBKAzPhotosHigh-End Date-916', 'datetime'),
						'MHBKAzPhotosHigh-Asset Count-917',
						'MHBKAzPhotosHigh-Summary Count-918',
						'MHBKAzPhotosHigh-Extended Count-919',
						'MHBKAzPhotosHigh-Day Group Assets Count-920',
						'MHBKAzPhotosHigh-Day Group Ext Assets Count-921',
						'MHBKAzPhotosHigh-Day Group Summary Assets Count-922',
						'MHBKAzPhotosHigh-Parent PH Key-923',
						'MHBKAzPhotosHigh-Year Key Asset-924',
						'MHBKAzPhotosHigh-Month First Asset-925',
						'MHBKAzPhotosHigh-Month Key Asset-926',
						'MHBKAzPhotosHigh-Key Asset-927',
						'MHBKAzPhotosHigh-Parent Day Group PH Key-928',
						'MHBKAzPhotosHigh-Day Group Key Asset-929',
						'MHBKAzPhotosHigh-is Curated-930',
						'MHBKAzPhotosHigh-Type-931',
						'MHBKAzPhotosHigh-Kind-932',
						'MHBKAzPhotosHigh-Category-933',
						'MHBKAzPhotosHigh-Visibility State-934',
						'MHBKAzPhotosHigh-Mood-935',
						'MHBKAzPhotosHigh-Enrichment State-936',
						'MHBKAzPhotosHigh-Enrichment Version-937',
						'MHBKAzPhotosHigh-Highlight Version-938',
						'zAsset-Year Highlight Being Key Asset-939',
						'YHBKAzPhotosHigh-UUID-940',
						'YHBKAzPhotosHigh-zPK-941',
						'YHBKAzPhotosHigh-zENT-942',
						'YHBKAzPhotosHigh-zOPT-943',
						'YHBKAzPhotosHigh-Promotion Score-944',
						'YHBKAzPhotosHigh-Title-945',
						'YHBKAzPhotosHigh-Subtitle-946',
						'YHBKAzPhotosHigh-Verbose Smart Description-947',
						('YHBKAzPhotosHigh-Start Date-948', 'datetime'),
						'YHBKAzPhotosHigh-Start Timezone Offset-949',
						'YHBKAzPhotosHigh-End Timezone Offset-950',
						('YHBKAzPhotosHigh-End Date-951', 'datetime'),
						'YHBKAzPhotosHigh-Asset Count-952',
						'YHBKAzPhotosHigh-Summary Count-953',
						'YHBKAzPhotosHigh-Extended Count-954',
						'YHBKAzPhotosHigh-Day Group Assets Count-955',
						'YHBKAzPhotosHigh-Day Group Ext Assets Count-956',
						'YHBKAzPhotosHigh-Day Group Summary Assets Count-957',
						'YHBKAzPhotosHigh-Parent PH Key-958',
						'YHBKAzPhotosHigh-Year Key Asset-959',
						'YHBKAzPhotosHigh-Month First Asset-960',
						'YHBKAzPhotosHigh-Month Key Asset-961',
						'YHBKAzPhotosHigh-Key Asset-962',
						'YHBKAzPhotosHigh-Parent Day Group PH Key-963',
						'YHBKAzPhotosHigh-Day Group Key Asset-964',
						'YHBKAzPhotosHigh-is Curated-965',
						'YHBKAzPhotosHigh-Type-966',
						'YHBKAzPhotosHigh-Kind-967',
						'YHBKAzPhotosHigh-Category-968',
						'YHBKAzPhotosHigh-Visibility State-969',
						'YHBKAzPhotosHigh-Mood-970',
						'YHBKAzPhotosHigh-Enrichment State-971',
						'YHBKAzPhotosHigh-Enrichment Version-972',
						'YHBKAzPhotosHigh-Highlight Version-973',
						'z3SuggBKA-3KeyAssets = zAsset-zPK-974',
						'z3SuggBKA-55SuggBeingKeyAssets = zSugg-zPK-975',
						'SBKAzSugg-zPK-976',
						'SBKAzSugg-UUID-977',
						('SBKAzSugg-Start Date-978', 'datetime'),
						'SBKAzSugg-State-979',
						'SBKAzSugg-Featured State-980',
						'SBKAzSugg-Notification State-981',
						('SBKAzSugg-Creation Date-982', 'datetime'),
						('SBKAzSugg-End Date-983', 'datetime'),
						('SBKAzSugg-Activation Date-984', 'datetime'),
						('SBKAzSugg-Expunge Date-985', 'datetime'),
						('SBKAzSugg-Relevant Until Date-986', 'datetime'),
						'SBKAzSugg-Title-987',
						'SBKAzSugg-Sub Title-988',
						'SBKAzSugg-Cached Count-989',
						'SBKAzSugg-Cahed Photos Count-990',
						'SBKAzSugg-Cached Videos Count-991',
						'SBKAzSugg-Type-992',
						'SBKAzSugg-Sub Type-993',
						'SBKAzSugg-Version-994',
						'SBKAzSugg-Cloud Local State-995',
						'SBKAzSugg-Cloud Delete State-996',
						'z3SuggBRA-3RepAssets1-997',
						'z3SuggBRA-55SuggBeingRepAssets-998',
						'SBRAzSugg-zPK-999',
						'SBRAzSugg-UUID-1000',
						('SBRAzSugg-Start Date-1001', 'datetime'),
						'SBRAzSugg-State-1002',
						'SBRAzSugg-Featured State-1003',
						'SBRAzSugg-Notification State-1004',
						('SBRAzSugg-Creation Date-1005', 'datetime'),
						('SBRAzSugg-End Date-1006', 'datetime'),
						('SBRAzSugg-Activation Date-1007', 'datetime'),
						('SBRAzSugg-Expunge Date-1008', 'datetime'),
						('SBRAzSugg-Relevant Until Date-1009', 'datetime'),
						'SBRAzSugg-Title-1010',
						'SBRAzSugg-Sub Title-1011',
						'SBRAzSugg-Cached Count-1012',
						'SBRAzSugg-Cahed Photos Count-1013',
						'SBRAzSugg-Cached Videos Count-1014',
						'SBRAzSugg-Type-1015',
						'SBRAzSugg-Sub Type-1016',
						'SBRAzSugg-Version-1017',
						'SBRAzSugg-Cloud Local State-1018',
						'SBRAzSugg-Cloud Delete State-1019',
						'zAsset-Highlight Visibility Score-1020',
						'zMedAnlyAstAttr-Media Analysis Version-1021',
						'zMedAnlyAstAttr-Audio Classification-1022',
						'zMedAnlyAstAttr-Best Video Range Duration Time Scale-1023',
						'zMedAnlyAstAttr-Best Video Range Start Time Scale-1024',
						'zMedAnlyAstAttr-Best Video Range Duration Value-1025',
						'zMedAnlyAstAttr-Best Video Range Start Value-1026',
						'zMedAnlyAstAttr-Packed Best Playback Rect-1027',
						'zMedAnlyAstAttr-Activity Score-1028',
						'zMedAnlyAstAttr-Video Score-1029',
						'zMedAnlyAstAttr-AutoPlay Suggestion Score-1030',
						'zMedAnlyAstAttr-Blurriness Score-1031',
						'zMedAnlyAstAttr-Exposure Score-1032',
						'zAssetAnalyState-Asset UUID-4TableStart-1033',
						'zAssetAnalyState-Analyisis State-1034',
						'zAssetAnalyState-Worker Flags-1035',
						'zAssetAnalyState-Worker Type-1036',
						('zAssetAnalyState-Ignore Until Date-1037', 'datetime'),
						('zAssetAnalyState-Last Ignored Date-1038', 'datetime'),
						('zAssetAnalyState-Sort Token-1039', 'datetime'),
						'zAsset-Overall Aesthetic Score-1040',
						'zCompAssetAttr-Behavioral Score-1041',
						'zCompAssetAttr-Failure Score zCompAssetAttr-1042',
						'zCompAssetAttr-Harmonious Color Score-1043',
						'zCompAssetAttr-Immersiveness Score-1044',
						'zCompAssetAttr-Interaction Score-1045',
						'zCompAssetAttr-Intersting Subject Score-1046',
						'zCompAssetAttr-Intrusive Object Presence Score-1047',
						'zCompAssetAttr-Lively Color Score-1048',
						'zCompAssetAttr-Low Light-1049',
						'zCompAssetAttr-Noise Score-1050',
						'zCompAssetAttr-Pleasant Camera Tilt Score-1051',
						'zCompAssetAttr-Pleasant Composition Score-1052',
						'zCompAssetAttr-Pleasant Lighting Score-1053',
						'zCompAssetAttr-Pleasant Pattern Score-1054',
						'zCompAssetAttr-Pleasant Perspective Score-1055',
						'zCompAssetAttr-Pleasant Post Processing Score-1056',
						'zCompAssetAttr-Pleasant Reflection Score-1057',
						'zCompAssetAttrPleasant Symmetry Score-1058',
						'zCompAssetAttr-Sharply Focused Subject Score-1059',
						'zCompAssetAttr-Tastfully Blurred Score-1060',
						'zCompAssetAttr-Well Chosen Subject Score-1061',
						'zCompAssetAttr-Well Framed Subject Score-1062',
						'zCompAssetAttr-Well Timeed Shot Score-1063',
						'zCldRes-Asset UUID-4TableStart-1064',
						'zCldRes-Cloud Local State-1065',
						'zCldRes-File Size-1066',
						'zCldRes-Height-1067',
						'zCldRes-Is Available-1068',
						'zCldRes-Is Locally Available-1069',
						'zCldRes-Prefetch Count-1070',
						'zCldRes-Source Type-1071',
						'zCldRes-Type-1072',
						'zCldRes-Width-1073',
						('zCldRes-Date Created-1074', 'datetime'),
						('zCldRes-Last OnDemand Download Date-1075', 'datetime'),
						('zCldRes-Last Prefetch Date-1076', 'datetime'),
						'zCldRes-Prunedat-1077',
						'zCldRes-File Path-1078',
						'zCldRes-Fingerprint-1079',
						'zCldRes-Item ID-1080',
						'zCldRes-UniID-1081',
						'zAddAssetAttr-zPK-1082',
						'zAddAssetAttr-zENT-1083',
						'ZAddAssetAttr-zOPT-1084',
						'zAddAssetAttr-zAsset= zAsset_zPK-1085',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-1086',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-1087',
						'zAddAssetAttr-Master Fingerprint-1088',
						'zAddAssetAttr-Public Global UUID-1089',
						'zAddAssetAttr-Deferred Photo Identifier-1090',
						'zAddAssetAttr-Original Assets UUID-1091',
						'zAddAssetAttr-Import Session ID-1092',
						'zAddAssetAttr-Originating Asset Identifier-1093',
						'zAddAssetAttr.Adjusted Fingerprint-1094',
						'zAlbumList-zPK= Album List Key-1095',
						'zAlbumList-zENT-1096',
						'zAlbumList-zOPT-1097',
						'zAlbumList-ID Key-1098',
						'zAlbumList-UUID-1099',
						'zAsset-zPK-1100',
						'zAsset-zENT-1101',
						'zAsset-zOPT-1102',
						'zAsset-Master= zCldMast-zPK-1103',
						'zAsset-Extended Attributes= zExtAttr-zPK-1104',
						'zAsset-Import Session Key-1105',
						'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-1106',
						'zAsset-FOK-Cloud Feed Asset Entry Key-1107',
						'zAsset-Moment Share Key= zShare-zPK-1108',
						'zAsset-zMoment Key= zMoment-zPK-1109',
						'zAsset-Computed Attributes Asset Key-1110',
						'zAsset-Highlight Being Assets-HBA Key-1111',
						'zAsset-Highlight Being Extended Assets-HBEA Key-1112',
						'zAsset-Highligh Being Summary Assets-HBSA Key-1113',
						'zAsset-Day Group Highlight Being Assets-DGHBA Key-1114',
						'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key-1115',
						'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key-1116',
						'zAsset-Promotion Score-1117',
						'zAsset-Media Analysis Attributes Key-1118',
						'zAsset-Media Group UUID-1119',
						'zAsset-UUID = store.cloudphotodb-1120',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-1121',
						'zAsset.Cloud Collection GUID-1122',
						'zAsset-Avalanche UUID-1123',
						'zAssetAnalyState-zPK-1124',
						'zAssetAnalyState-zEnt-1125',
						'zAssetAnalyState-zOpt-1126',
						'zAssetAnalyState-Asset= zAsset-zPK-1127',
						'zAssetAnalyState-Asset UUID-1128',
						'zAssetDes-zPK-1129',
						'zAssetDes-zENT-1130',
						'zAssetDes-zOPT-1131',
						'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK-1132',
						'zCldFeedEnt-zPK= zCldShared keys-1133',
						'zCldFeedEnt-zENT-1134',
						'zCldFeedEnt-zOPT-1135',
						'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-1136',
						'zCldFeedEnt-Entry Invitation Record GUID-1137',
						'zCldFeedEnt-Entry Cloud Asset GUID-1138',
						'zCldMast-zPK= zAsset-Master-1139',
						'zCldMast-zENT-1140',
						'zCldMast-zOPT-1141',
						'zCldMast-Moment Share Key= zShare-zPK-1142',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-1143',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-1144',
						'zCldMast-Originating Asset ID-1145',
						'zCldMast-Import Session ID- AirDrop-StillTesting-1146',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-1147',
						'CMzCldMastMedData-zENT-1148',
						'CMzCldMastMedData-zOPT-1149',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-1150',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-1151',
						'AAAzCldMastMedData-zENT-1152',
						'AAAzCldMastMedData-zOPT-1153',
						'AAAzCldMastMedData-CldMast key-1154',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-1155',
						'zCldRes-zPK-1156',
						'zCldRes-zENT-1157',
						'zCldRes-zOPT-1158',
						'zCldRes-Asset= zAsset-zPK-1159',
						'zCldRes-Cloud Master= zCldMast-zPK-1160',
						'zCldRes-Asset UUID-1161',
						'zCldShareAlbumInvRec-zPK-1162',
						'zCldShareAlbumInvRec-zEnt-1163',
						'zCldShareAlbumInvRec-zOpt-1164',
						'zCldShareAlbumInvRec-Album Key-1165',
						'zCldShareAlbumInvRec-FOK Album Key-1166',
						'zCldShareAlbumInvRec-Album GUID-1167',
						'zCldShareAlbumInvRec-Cloud GUID-1168',
						'zCldSharedComment-zPK-1169',
						'zCldSharedComment-zENT-1170',
						'zCldSharedComment-zOPT-1171',
						'zCldSharedComment-Commented Asset Key= zAsset-zPK-1172',
						'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-1173',
						'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-1174',
						'zCldSharedComment-Liked Asset Key= zAsset-zPK-1175',
						'zCldSharedComment-CldFeedLikeCommentEntry Key-1176',
						'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-1177',
						'zCldSharedComment-Cloud GUID-1178',
						'zCompAssetAttr-zPK-1179',
						'zCompAssetAttr-zEnt-1180',
						'zCompAssetAttr-zOpt-1181',
						'zCompAssetAttr-Asset Key-1182',
						'zDetFace-zPK-1183',
						'zDetFace-zEnt-1184',
						'zDetFace.zOpt-1185',
						'zDetFace-Asset= zAsset-zPK or Asset Containing Face-1186',
						'zDetFace-Person= zPerson-zPK-1187',
						'zDetFace-Person Being Key Face-1188',
						'zDetFace-Face Print-1189',
						'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-1190',
						'zDetFace-FaceGroup= zDetFaceGroup-zPK-1191',
						'zDetFace-UUID-1192',
						'zDetFaceGroup-zPK-1193',
						'zDetFaceGroup-zENT-1194',
						'zDetFaceGroup-zOPT-1195',
						'zDetFaceGroup-AssocPerson= zPerson-zPK-1196',
						'zDetFaceGroup-KeyFace= zDetFace-zPK-1197',
						'zDetFaceGroup-UUID-1198',
						'zDetFacePrint-zPK-1199',
						'zDetFacePrint-zEnt-1200',
						'zDetFacePrint-zOpt-1201',
						'zDetFacePrint-Face Key-1202',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-1203',
						'zExtAttr-zENT-1204',
						'zExtAttr-zOPT-1205',
						'zExtAttr-Asset Key-1206',
						'zFaceCrop-zPK-1207',
						'zFaceCrop-zEnt-1208',
						'zFaceCrop-zOpt-1209',
						'zFaceCrop-Asset Key-1210',
						'zFaceCrop-Invalid Merge Canidate Person UUID-1211',
						'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-1212',
						'zFaceCrop-Face Key-1213',
						'zFaceCrop-UUID-1214',
						'zGenAlbum-zPK=26AlbumLists= 26Albums-1215',
						'zGenAlbum-zENT-1216',
						'zGenAlbum-zOpt-1217',
						'zGenAlbum-Key Asset-Key zAsset-zPK-1218',
						'zGenAlbum-Secondary Key Asset-1219',
						'zGenAlbum-Tertiary Key Asset-1220',
						'zGenAlbum-Custom Key Asset-1221',
						'zGenAlbum-Parent Folder Key= zGenAlbum-zPK-1222',
						'zGenAlbum-FOK Parent Folder-1223',
						'zGenAlbum-UUID-1224',
						'zGenAlbum-Cloud_GUID = store.cloudphotodb-1225',
						'zGenAlbum-Project Render UUID-1226',
						'zIntResou-zPK-1227',
						'zIntResou-zENT-1228',
						'zIntResou-zOPT-1229',
						'zIntResou-Asset= zAsset_zPK-1230',
						'zIntResou-Fingerprint-1231',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-1232',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-1233',
						'zMedAnlyAstAttr-zEnt-1234',
						'zMedAnlyAstAttr-zOpt-1235',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-1236',
						'zPerson-zPK=zDetFace-Person-1237',
						'zPerson-zEnt-1238',
						'zPerson-zOpt-1239',
						'zPerson-KeyFace=zDetFace-zPK-1240',
						'zPerson-Assoc Face Group Key-1241',
						'zPerson-Person UUID-1242',
						'zSceneP-zPK-1243',
						'zSceneP-zENT-1244',
						'zSceneP-zOPT-1245',
						'zShare-zPK-1246',
						'zShare-zENT-1247',
						'zShare-zOPT-1248',
						'zShare-UUID-1249',
						'SPLzShare-UUID-1250',
						'zShare-Scope ID = store.cloudphotodb-1251',
						'zSharePartic-zPK-1252',
						'zSharePartic-zENT-1253',
						'zSharePartic-zOPT-1254',
						'zSharePartic-Share Key= zShare-zPK-1255',
						'zSharePartic-UUID-1256',
						'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key-1257',
						'zUnmAdj-zOPT-1258',
						'zUnmAdj-zENT-1259',
						'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK-1260',
						'zUnmAdj-UUID-1261',
						'zUnmAdj-Other Adjustments Fingerprint-1262',
						'zUnmAdj-Similar to Orig Adjustments Fingerprint-1263',
						'z25AlbumList-25Albums= zGenAlbum-zPK-1264',
						'z25AlbumList-Album List Key-1265',
						'z25AlbumList-FOK25Albums Key-1266',
						'z26Assets-26Albums= zGenAlbum-zPK-1267',
						'z26Assets-3Asset Key= zAsset-zPK in the Album-1268',
						'z26Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY-1269')
		data_list = get_sqlite_db_records(source_path, query)

		return data_headers, data_list, source_path
