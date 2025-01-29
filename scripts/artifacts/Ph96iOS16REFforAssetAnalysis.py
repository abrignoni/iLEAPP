__artifacts_v2__ = {
	'Ph96_1iOS16RefforAssetAnalysisPhDaPsql': {
		'name': 'Ph96.1-iOS16_Ref_for_Asset_Analysis-PhDaPsql',
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
		"output_types": ["standard", "tsv", "none"]
	},
	'Ph96_2iOS16RefforAssetAnalysisSyndPL': {
		'name': 'Ph96.2-iOS16_Ref_for_Asset_Analysis-SyndPL',
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
def Ph96_1iOS16RefforAssetAnalysisPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
	for source_path in files_found:
		source_path = str(source_path)

		if source_path.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if (version.parse(iosversion) <= version.parse("15.8.2")) or (version.parse(iosversion) >= version.parse("17")):
		logfunc(f"Unsupported version for PhotoData-Photos.sqlite for iOS " + iosversion)
		return (), [], source_path
	if (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
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
		CASE zAsset.ZBUNDLESCOPE
			WHEN 0 THEN '0-WheniCldPhtos-ON-AssetNotInSharedAlbum_or_WheniCldPhtos-OFF-AssetOnLocalDevice-0'
			WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
			WHEN 2 THEN '2-WheniCldPhtos-ON-AssetInCloudSharedAlbum-2'
			WHEN 3 THEN '3-WheniCldPhtos-ON-AssetIsInSWYConversation-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
		END AS 'zAsset-Bundle Scope',
		CASE zAsset.ZSYNDICATIONSTATE
			WHEN 0 THEN '0-LPLPs-NA_or_SYWPs-Received-SWY_Synd_Asset-0'
			WHEN 1 THEN '1-SWYPs-Sent-SWY_Synd_Asset-1'
			WHEN 2 THEN '2-SWYPs-Manually-Saved_SWY_Synd_Asset-2'
			WHEN 3 THEN '3-SWYPs-STILLTESTING_Sent-SWY-3'
			WHEN 8 THEN '8-SWYPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
			WHEN 9 THEN '9-SWYPs-STILLTESTING_Sent_SWY-9'
			WHEN 10 THEN '10-SWYPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
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
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
		CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
			WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
			WHEN 1 THEN '1-Asset-In-Active-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
		END AS 'zAsset-Active Library Scope Participation State -4QueryStart',
		CASE zAsset.ZLIBRARYSCOPESHARESTATE
			WHEN 0 THEN '0-Asset-Not-In-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
		END AS 'zAsset-Library Scope Share State- StillTesting -4QueryStart',
		zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count-SPL -4QueryStart',
		zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count-SPL -4QueryStart',
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
		SWYConverszGenAlbum.ZUUID AS 'SWYConverszGenAlbum-UUID-4QueryStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4QueryStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4QueryStart',
		SWYConverszGenAlbum.ZCLOUDGUID AS 'SWYConverszGenAlbum-Cloud GUID-4QueryStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4QueryStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4QueryStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4QueryStart',
		SWYConverszGenAlbum.ZPROJECTRENDERUUID AS 'SWYConverszGenAlbum-Project Render UUID-4QueryStart',
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
		CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud_Local_State-4QueryStart',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Creation Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Cloud Creation Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- Cloud Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Start Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- Start Date- 4QueryStart',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- End Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- End Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Subscription Date- 4QueryStart',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title- 4QueryStart',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied- 4QueryStart',
		SWYConverszGenAlbum.ZTITLE AS 'SWYConverszGenAlbum- Title -User&System Applied- 4QueryStart',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY- 4QueryStart',
		zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK -4QueryStart',
		SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY- 4QueryStart',
		zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier- 4QueryStart',
		SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier- 4QueryStart',
		CASE SWYConverszGenAlbum.ZSYNDICATE
			WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
		END AS 'SWYConverszGenAlbum- Syndicate-4QueryStart',
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
		CASE SWYConverszGenAlbum.ZKIND
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
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
		END AS 'SWYConverszGenAlbum-Album Kind- 4QueryStart',		
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
		zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
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
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK-4QueryStart',
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
		zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',
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
		zPhotoAnalysisAssetAttr.ZWALLPAPERPROPERTIESVERSION AS 'zPhotoAnalysisAssetAttr-Wallpaper Properties Version',
		DateTime(zPhotoAnalysisAssetAttr.ZWALLPAPERPROPERTIESTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zPhotoAnalysisAssetAttr-Wallpaper Properties Timestamp',
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
		CASE zAsset.ZLIBRARYSCOPESHARESTATE
			WHEN 0 THEN '0-Asset-Not-In-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
		END AS 'zAsset-Library Scope Share State- StillTesting',
		CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
			WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
			WHEN 1 THEN '1-Asset-In-Active-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
		END AS 'zAsset-Active Library Scope Participation State',
		zAddAssetAttr.ZLIBRARYSCOPEASSETCONTRIBUTORSTOUPDATE AS 'zAddAssetAttr-Library Scope Asset Contributors To Update',
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
		CASE zSharePartic.Z54_SHARE
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.Z54_SHARE || ''
		END AS 'zSharePartic-z54SHARE',
		CASE SPLzSharePartic.Z54_SHARE
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.Z54_SHARE || ''
		END AS 'SPLzSharePartic-z54SHARE',
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
		zShare.ZCLOUDITEMCOUNT AS 'zShare-Cloud Item Count-CMM',
		SPLzShare.ZCLOUDITEMCOUNT AS 'SPLzShare-Cloud Item Count-SPL',
		zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
		SPLzShare.ZASSETCOUNT AS 'SPLzShare-Asset Count-SPL',
		zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count-CMM',
		SPLzShare.ZCLOUDPHOTOCOUNT AS 'SPLzShare-Cloud Photo Count-SPL',
		zShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-CMM',
		SPLzShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'SPLzShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-SPL',
		zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
		SPLzShare.ZPHOTOSCOUNT AS 'SPLzShare-Photos Count-CMM-SPL',
		zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
		SPLzShare.ZUPLOADEDPHOTOSCOUNT AS 'SPLzShare-Uploaded Photos Count-SPL',
		zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count-CMM',
		SPLzShare.ZCLOUDVIDEOCOUNT AS 'SPLzShare-Cloud Video Count-SPL',
		zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
		SPLzShare.ZVIDEOSCOUNT AS 'SPLzShare-Videos Count-SPL',
		zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
		SPLzShare.ZUPLOADEDVIDEOSCOUNT AS 'SPLzShare-Uploaded Videos Count-SPL',
		zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',
		SPLzShare.ZFORCESYNCATTEMPTED AS 'SPLzShare-Force Sync Attempted-SPL',
		CASE zShare.ZCLOUDLOCALSTATE
			WHEN 1 THEN '1-LocalandCloud-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDLOCALSTATE || ''
		END AS 'zShare-Cloud Local State-CMM',
		CASE SPLzShare.ZCLOUDLOCALSTATE
			WHEN 1 THEN '1-LocalandCloud-SPL-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZCLOUDLOCALSTATE || ''
		END AS 'SPLzShare-Cloud Local State-SPL',
		CASE zShare.ZSCOPESYNCINGSTATE
			WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPESYNCINGSTATE || ''
		END AS 'zShare-Scope Syncing State-CMM',
		CASE SPLzShare.ZSCOPESYNCINGSTATE
			WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSCOPESYNCINGSTATE || ''
		END AS 'SPLzShare-Scope Syncing State-SPL',
		CASE zShare.ZAUTOSHAREPOLICY
			WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZAUTOSHAREPOLICY || ''
		END AS 'zShare-Auto Share Policy-CMM',
		CASE SPLzShare.ZAUTOSHAREPOLICY
			WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZAUTOSHAREPOLICY || ''
		END AS 'SPLzShare-Auto Share Policy-SPL',
		CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-CMM-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'zShare-Should Notify On Upload Completion-CMM',
		CASE SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-SPL-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'SPLzShare-Should Notify On Upload Completion-SPL',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK-SPL-CMM',
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
		DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date-CMM',
		DateTime(SPLzShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Trashed Date-SPL',
		DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-LastParticipant Asset Trash Notification Date-CMM',
		DateTime(SPLzShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-LastParticipant Asset Trash Notification Date-SPL',
		DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Last Participant Asset Trash Notification View Date-CMM',
		DateTime(SPLzShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Last Participant Asset Trash Notification View Date-SPL',
		CASE zShare.ZEXITSOURCE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSOURCE || ''
		END AS 'zShare-Exit Source-CMM',
		CASE SPLzShare.ZEXITSOURCE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZEXITSOURCE || ''
		END AS 'SPLzShare-Exit Source-SPL',
		CASE zShare.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSTATE || ''
		END AS 'zShare-SPL_Exit State-CMM',
		CASE SPLzShare.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZEXITSTATE || ''
		END AS 'SPLzShare-SPL_Exit State-SPL',
		CASE zShare.ZEXITTYPE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zShare.ZEXITTYPE || ''
		END AS 'zShare-Exit Type-CMM',
		CASE SPLzShare.ZEXITTYPE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZEXITTYPE || ''
		END AS 'SPLzShare-Exit Type-SPL',
		CASE zShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'zShare-Should Ignor Budgets-CMM',
		CASE SPLzShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'SPLzShare-Should Ignor Budgets-SPL',
		CASE zShare.ZPREVIEWSTATE
			WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZPREVIEWSTATE || ''
		END AS 'zShare-Preview State-CMM',
		CASE SPLzShare.ZPREVIEWSTATE
			WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZPREVIEWSTATE || ''
		END AS 'SPLzShare-Preview State-SPL',
		zShare.ZPREVIEWDATA AS 'zShare-Preview Data-CMM',
		SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview Data-SPL',
		zShare.ZRULESDATA AS 'zShare-Rules-CMM',
		SPLzShare.ZRULESDATA AS 'SPLzShare-Rules-SPL',
		zShare.ZTHUMBNAILIMAGEDATA AS 'zShare-Thumbnail Image Data-CMM',
		SPLzShare.ZTHUMBNAILIMAGEDATA AS 'SPLzShare-Thumbnail Image Data-SPL',
		CASE zShare.ZPARTICIPANTCLOUDUPDATESTATE
			WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
			ELSE 'Unknown-New-Value!: ' || zShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
		END AS 'zShare-Participant Cloud Update State-CMM',
		CASE SPLzShare.ZPARTICIPANTCLOUDUPDATESTATE
			WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
		END AS 'SPLzShare-Participant Cloud Update State-SPL',
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
			WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
			WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
		END AS 'zSharePartic-Is Current User',
		CASE SPLzSharePartic.ZISCURRENTUSER
			WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
			WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
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
		zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
		SPLzSharePartic.ZPARTICIPANTID AS 'SPLzSharePartic-Participant ID',
		zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
		SPLzSharePartic.ZUSERIDENTIFIER AS 'SPLzSharePartic-User ID',
		zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK-4TableStart',
		SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK-4TableStart',
		zSharePartic.Z_PK AS 'zSharePartic-zPK-4TableStart',
		zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
		SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
		zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
		SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
		CASE zSharePartic.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZEXITSTATE || ''
		END AS 'zSharePartic-Exit State',
		CASE SPLzSharePartic.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZEXITSTATE || ''
		END AS 'SPLzSharePartic-Exit State',
		ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID-4TableStart',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
		SWYConverszGenAlbum.ZUUID AS 'SWYConverszGenAlbum-UUID-4TableStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4TableStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart',
		SWYConverszGenAlbum.ZCLOUDGUID AS 'SWYConverszGenAlbum-Cloud GUID-4TableStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4TableStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4TableStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4TableStart',
		SWYConverszGenAlbum.ZPROJECTRENDERUUID AS 'SWYConverszGenAlbum-Project Render UUID-4TableStart',
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
		CASE SWYConverszGenAlbum.ZKIND
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
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
		END AS 'SWYConverszGenAlbum-Album Kind',
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
		CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud_Local_State',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
		SWYConverszGenAlbum.ZTITLE AS 'SWYConverszGenAlbum- Title -User&System Applied',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY',
		zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
		SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
		zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',
		SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
		CASE SWYConverszGenAlbum.ZSYNDICATE
			WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
		END AS 'SWYConverszGenAlbum- Syndicate',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
		DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Creation Date',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
		DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
		DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Subscription Date',
		ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
		zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',
		SWYConverszGenAlbum.ZPENDINGITEMSCOUNT AS 'SWYConverszGenAlbum-Pending Items Count',
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
		CASE SWYConverszGenAlbum.ZPENDINGITEMSTYPE
			WHEN 1 THEN 'No-1'
			WHEN 24 THEN '24-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPENDINGITEMSTYPE || ''
		END AS 'SWYConverszGenAlbum-Pending Items Type',
		zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
		SWYConverszGenAlbum.ZCACHEDPHOTOSCOUNT AS 'SWYConverszGenAlbum- Cached Photos Count',
		zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',
		SWYConverszGenAlbum.ZCACHEDVIDEOSCOUNT AS 'SWYConverszGenAlbum- Cached Videos Count',
		zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
		SWYConverszGenAlbum.ZCACHEDCOUNT AS 'SWYConverszGenAlbum- Cached Count',
		ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
		zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',
		SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
		CASE zGenAlbum.ZHASUNSEENCONTENT
			WHEN 0 THEN 'No Unseen Content-StillTesting-0'
			WHEN 1 THEN 'Unseen Content-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
		END AS 'zGenAlbum-Has Unseen Content',
		CASE SWYConverszGenAlbum.ZHASUNSEENCONTENT
			WHEN 0 THEN 'No Unseen Content-StillTesting-0'
			WHEN 1 THEN 'Unseen Content-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZHASUNSEENCONTENT || ''
		END AS 'SWYConverszGenAlbum-Has Unseen Content',
		zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',
		SWYConverszGenAlbum.ZUNSEENASSETSCOUNT AS 'SWYConverszGenAlbum-Unseen Asset Count',
		CASE zGenAlbum.ZISOWNED
			WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
			WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
		END AS 'zGenAlbum-is Owned',
		CASE SWYConverszGenAlbum.ZISOWNED
			WHEN 0 THEN 'SWYConverszGenAlbum-Not Owned by Device Apple Acnt-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Owned by Device Apple Acnt-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISOWNED || ''
		END AS 'SWYConverszGenAlbum-is Owned',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
			WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
			WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
		END AS 'zGenAlbum-Cloud Relationship State',
		CASE SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATE
			WHEN 0 THEN 'SWYConverszGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
			WHEN 2 THEN 'SWYConverszGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud Relationship State',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
			WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
		END AS 'zGenAlbum-Cloud Relationship State Local',
		CASE SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
			WHEN 0 THEN 'SWYConverszGenAlbum-Shared Album Accessible Local Device-0'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
		END AS 'SWYConverszGenAlbum-Cloud Relationship State Local',
		zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',
		SWYConverszGenAlbum.ZCLOUDOWNEREMAILKEY AS 'SWYConverszGenAlbum-Cloud Owner Mail Key',
		zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',
		SWYConverszGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'SWYConverszGenAlbum-Cloud Owner Frist Name',
		zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',
		SWYConverszGenAlbum.ZCLOUDOWNERLASTNAME AS 'SWYConverszGenAlbum-Cloud Owner Last Name',
		zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
		SWYConverszGenAlbum.ZCLOUDOWNERFULLNAME AS 'SWYConverszGenAlbum-Cloud Owner Full Name',
		zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',
		SWYConverszGenAlbum.ZCLOUDPERSONID AS 'SWYConverszGenAlbum-Cloud Person ID',
		zAsset.ZCLOUDOWNERHASHEDPERSONID AS 'zAsset-Cloud Owner Hashed Person ID',
		zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',
		SWYConverszGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'SWYConverszGenAlbum-Cloud Owner Hashed Person ID',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
		END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
			WHEN 0 THEN 'SWYConverszGenAlbum-Local Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Local Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
		END AS 'SWYConverszGenAlbum-Local Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
		END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
			WHEN 0 THEN 'SWYConverszGenAlbum-Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
		END AS 'SWYConverszGenAlbum-Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
			WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
		END AS 'zGenAlbum-Cloud Album Sub Type',
		CASE SWYConverszGenAlbum.ZCLOUDALBUMSUBTYPE
			WHEN 0 THEN 'SWYConverszGenAlbum Multi-Contributor-0'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDALBUMSUBTYPE || ''
		END AS 'SWYConverszGenAlbum-Cloud Album Sub Type',
		DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Contribution Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Contribution Date',
		DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Last Interesting Change Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Last Interesting Change Date',
		CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
		END AS 'zGenAlbum-Cloud Notification Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDNOTIFICATIONSENABLED
			WHEN 0 THEN 'SWYConverszGenAlbum-Cloud Notifications Disabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Cloud Notifications Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
		END AS 'SWYConverszGenAlbum-Cloud Notification Enabled',
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
		CASE SWYConverszGenAlbum.ZISPINNED
			WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
		END AS 'SWYConverszGenAlbum-Pinned',
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
		CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
			WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
			WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
			WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
		END AS 'SWYConverszGenAlbum-Custom Sort Key',
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
		CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
			WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
			WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
		END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
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
		CASE SWYConverszGenAlbum.ZISPROTOTYPE
			WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
		END AS 'SWYConverszGenAlbum-Is Prototype',
		CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'ParentzGenAlbum-Project Document Type',
		CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'zGenAlbum-Project Document Type',
		CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'SWYConverszGenAlbum-Project Document Type',
		CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'ParentzGenAlbum-Custom Query Type',
		CASE zGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'zGenAlbum-Custom Query Type',
		CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'SWYConverszGenAlbum-Custom Query Type',
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
		CASE SWYConverszGenAlbum.ZTRASHEDSTATE
			WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
		END AS 'SWYConverszGenAlbum-Trashed State',
		DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
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
		CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud Delete State',
		CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
			WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
			WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
		END AS 'zGenAlbum-Cloud Owner Whitelisted',
		CASE SWYConverszGenAlbum.ZCLOUDOWNERISWHITELISTED
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Owner Not Whitelisted-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Owner Whitelisted-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
		END AS 'SWYConverszGenAlbum-Cloud Owner Whitelisted',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
		END AS 'zGenAlbum-Cloud Local Public URL Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Local Public URL Disabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Local has Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
		END AS 'SWYConverszGenAlbum-Cloud Local Public URL Enabled',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
			WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
		END AS 'zGenAlbum-Cloud Public URL Enabled',
		zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',
		CASE SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLED
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Public URL Disabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLED || ''
		END AS 'SWYConverszGenAlbum-Cloud Public URL Enabled',
		SWYConverszGenAlbum.ZPUBLICURL AS 'SWYConverszGenAlbum-Public URL',
		zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',
		SWYConverszGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'SWYConverszGenAlbum-Key Asset Face Thumb Index',
		zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',
		SWYConverszGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'SWYConverszGenAlbum-Project Text Extension ID',
		zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',
		SWYConverszGenAlbum.ZUSERQUERYDATA AS 'SWYConverszGenAlbum-User Query Data',
		zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
		SWYConverszGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'SWYConverszGenAlbum-Custom Query Parameters',
		zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
		SWYConverszGenAlbum.ZPROJECTDATA AS 'SWYConverszGenAlbum-Project Data',
		CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'zGenAlbum-Search Index Rebuild State',
		CASE SWYConverszGenAlbum.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'SWYConverszGenAlbum-Search Index Rebuild State',
		CASE zGenAlbum.ZDUPLICATETYPE
			WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
			WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
			WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
		END AS 'zGenAlbum-Duplicate Type',
		CASE SWYConverszGenAlbum.ZDUPLICATETYPE
			WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
			WHEN 1 THEN '1-Duplicate Asset_Pending-Merge-1'
			WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZDUPLICATETYPE || ''
		END AS 'SWYConverszGenAlbum-Duplicate Type',
		CASE zGenAlbum.ZPRIVACYSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
		END AS 'zGenAlbum-Privacy State',
		CASE SWYConverszGenAlbum.ZPRIVACYSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
		END AS 'SWYConverszGenAlbum-Privacy State',
		zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID-4TableStart',
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
		zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
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
		CASE zDetFace.ZETHNICITYTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Black-African American-1'
			WHEN 2 THEN 'White-2'
			WHEN 3 THEN 'Hispanic-Latino-3'
			WHEN 4 THEN 'Asian-4'
			WHEN 5 THEN 'Native Hawaiian-Other Pacific Islander-5'
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
			WHEN 1 THEN 'Black-Brown Hair Color-1'
			WHEN 2 THEN 'Brown-Blonde Hair Color-2'
			WHEN 3 THEN 'Brown-Red Hair Color-3'
			WHEN 4 THEN 'Red-White Hair Color-4'
			WHEN 5 THEN 'StillTesting-Artifical-5'
			WHEN 6 THEN 'White-Bald Hair Color-6'
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
			WHEN 1 THEN 'Disgusted-Angry-1'
			WHEN 2 THEN 'Suprised-Fearful-2'
			WHEN 3 THEN 'Neutral-3'
			WHEN 4 THEN 'Confident-Smirk-4'
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
		zAsset.ZHIGHLIGHTVISIBILITYSCORE AS 'zAsset-Highlight Visibility Score',
		zMemory.ZUUID AS 'zMemory-UUID-4TableStart',
		zMemory.ZASSETLISTPREDICATE AS 'zMemory-AssetListPredicte',
		zMemory.ZSCORE AS 'zMemory-Score',
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
		DateTime(zMemory.ZLASTENRICHMENTDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Enrichment Date',
		CASE zMemory.ZUSERACTIONOPTIONS
			WHEN 0 THEN 'User Actions Options Memory Not User Created-0'
			WHEN 1 THEN 'User Actions Options Memory User Created-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZUSERACTIONOPTIONS || ''
		END AS 'zMemory-User Action Options',
		CASE zMemory.ZFAVORITE
			WHEN 0 THEN 'Memory Not Favorite-0'
			WHEN 1 THEN 'Memory Favorite-1'
		END AS 'zMemory-Favorite Memory',
		zMemory.ZVIEWCOUNT AS 'zMemory-View Count',
		zMemory.ZPLAYCOUNT AS 'zMemory-Play Count',
		zMemory.ZREJECTED AS 'zMemory-Rejected',
		zMemory.ZSHARECOUNT AS 'zMemory-Share Count',
		zMemory.ZSHARINGCOMPOSITION AS 'zMemory-Sharing Composition',
		DateTime(zMemory.ZLASTMOVIEPLAYEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Movie Play Date',
		DateTime(zMemory.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Viewed Date',
		zMemory.ZPENDINGPLAYCOUNT AS 'zMemory-Pending Play Count Memory',
		zMemory.ZPENDINGSHARECOUNT AS 'zMemory-Pending Share Count Memory',
		zMemory.ZPENDINGVIEWCOUNT AS 'zMemory-Pending View Count Memory',
		zMemory.ZPENDINGSTATE AS 'zMemory-Pending State',
		CASE zMemory.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZFEATUREDSTATE || ''
		END AS 'zMemory-Featured State',
		zMemory.ZPHOTOSGRAPHVERSION AS 'zMemory-Photos Graph Version',
		zMemory.ZGRAPHMEMORYIDENTIFIER AS 'zMemory-Graph Memory Identifier',
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
		CASE zMemory.ZSTORYCOLORGRADEKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSTORYCOLORGRADEKIND || ''
		END AS 'zMemory-Story Color Grade Kind',
		CASE zMemory.ZSTORYSERIALIZEDTITLECATEGORY
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSTORYSERIALIZEDTITLECATEGORY || ''
		END AS 'zMemory-Story Serialized Title Category',
		CASE zMemory.ZSYNDICATEDCONTENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSYNDICATEDCONTENTSTATE || ''
		END AS 'zMemory-Syndicated Content State',
		CASE zMemory.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting Memory-Search Index State-0'
			WHEN 1 THEN '1-StillTesting Memory-Search Index State-1'
			WHEN 2 THEN '2-StillTesting Memory-Search Index State-2'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'zMemory-Search Index Rebuild State',
		zMemory.ZBLACKLISTEDFEATURE AS 'zMemory-Black Listed Feature',
		zMoment.ZUUID AS 'zMoment-UUID-4TableStart',
		zMoment.ZAGGREGATIONSCORE AS 'zMoment-Aggregation Score',
		DateTime(zMoment.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Start Date',
		DateTime(zMoment.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Representative Date',
		zMoment.ZTIMEZONEOFFSET AS 'zMoment-Timezone Offset',
		DateTime(zMoment.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Modification Date',
		DateTime(zMoment.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-End Date',
		zMoment.ZSUBTITLE AS 'zMoment-SubTitle',
		zMoment.ZTITLE AS 'zMoment-Title',
		CASE zMoment.ZORIGINATORSTATE
			WHEN 0 THEN '0-StillTesting Moment-Originator_State-0'
			WHEN 1 THEN '1-StillTesing Moment-Originator_State-1'
			WHEN 2 THEN '2-StillTesting Moment-Originator_State-2'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZORIGINATORSTATE || ''
		END AS 'zMoment-Originator State',
		CASE zMoment.ZSHARINGCOMPOSITION
			WHEN 0 THEN '0-StillTesting Moment-Sharing_Compo-0'
			WHEN 1 THEN '1-StillTesting Moment-Sharing_Compo-1'
			WHEN 2 THEN '2-StillTesting Moment-Sharing_Compo-2'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZSHARINGCOMPOSITION || ''
		END AS 'zMoment-Sharing Composition',
		zMoment.ZCACHEDCOUNTSHARED AS 'zMoment-Cached Count Shared',
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
			ELSE zMoment.ZGPSHORIZONTALACCURACY
		END AS 'zMoment-GPS Horizontal Accuracy',
		zMoment.ZCACHEDCOUNT AS 'zMoment-Cache Count',
		zMoment.ZCACHEDPHOTOSCOUNT AS 'zMoment-Cached Photos Count',
		zMoment.ZCACHEDVIDEOSCOUNT AS 'zMoment-Cached Videos Count',
		CASE zMoment.ZTRASHEDSTATE
			WHEN 0 THEN 'zMoment Not In Trash-0'
			WHEN 1 THEN 'zMoment In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZTRASHEDSTATE || ''
		END AS 'zMoment-Trashed State',
		SBKAzSugg.ZUUID AS 'SBKAzSugg-UUID-4TableStart',
		SBKAzSugg.ZSUGGESTIONCONTEXT AS 'SBKAzSugg-Suggestion Context',
		SBKAzSugg.ZSHARINGCOMPOSITION AS 'SBKAzSugg-Sharing Composition',
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
		SBKAzSugg.ZACTIONDATA AS 'SBKAzSugg-Action Data',
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
		SBRAzSugg.ZUUID AS 'SBRAzSugg-UUID-4TableStart',
		SBRAzSugg.ZSUGGESTIONCONTEXT AS 'SBRAzSugg-Suggestion Context',
		SBRAzSugg.ZSHARINGCOMPOSITION AS 'SBRAzSugg-Sharing Composition',
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
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZTYPE || ''
		END AS 'SBRAzSugg-Type',
		CASE SBRAzSugg.ZSUBTYPE
			WHEN 501 THEN '501-StillTesting'
			WHEN 502 THEN '502-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZSUBTYPE || ''
		END AS 'SBRAzSugg-Sub Type',
		SBRAzSugg.ZACTIONDATA AS 'SBRAzSugg-Action Data',
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
		zMedAnlyAstAttr.ZMEDIAANALYSISVERSION AS 'zMedAnlyAstAttr-Media Analysis Version',
		zMedAnlyAstAttr.ZAUDIOCLASSIFICATION AS 'zMedAnlyAstAttr-Audio Classification',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Duration Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Start Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONVALUE AS 'zMedAnlyAstAttr-Best Video Range Duration Value',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTVALUE AS 'zMedAnlyAstAttr-Best Video Range Start Value',
		zMedAnlyAstAttr.ZPACKEDBESTPLAYBACKRECT AS 'zMedAnlyAstAttr-Packed Best Playback Rect',
		zMedAnlyAstAttr.ZACTIVITYSCORE AS 'zMedAnlyAstAttr-Activity Score',
		zMedAnlyAstAttr.ZVIDEOSCORE AS 'zMedAnlyAstAttr-Video Score',
		zMedAnlyAstAttr.ZAUDIOSCORE AS 'zMedAnlyAstAttr-Audio Score',
		zMedAnlyAstAttr.ZWALLPAPERSCORE AS 'zMedAnlyAstAttr-Wallpaper Score',
		zMedAnlyAstAttr.ZAUTOPLAYSUGGESTIONSCORE AS 'zMedAnlyAstAttr-AutoPlay Suggestion Score',
		zMedAnlyAstAttr.ZBLURRINESSSCORE AS 'zMedAnlyAstAttr-Blurriness Score',
		zMedAnlyAstAttr.ZEXPOSURESCORE AS 'zMedAnlyAstAttr-Exposure Score',
		zMedAnlyAstAttr.ZPROBABLEROTATIONDIRECTIONCONFIDENCE AS 'zMedAnlyAstAttr-Probable Rotation Direction Confidence',
		zMedAnlyAstAttr.ZPROBABLEROTATIONDIRECTION AS 'zMedAnlyAstAttr-Probable Rotation Direction',
		zMedAnlyAstAttr.ZSCREENTIMEDEVICEIMAGESENSITIVITY AS 'zMedAnlyAstAttr-Screen Time Device Image Sensitivity',
		zAssetAnalyState.ZASSETUUID AS 'zAssetAnalyState-Asset UUID-4TableStart',
		zAssetAnalyState.ZANALYSISSTATE AS 'zAssetAnalyState-Analyisis State',
		zAssetAnalyState.ZWORKERFLAGS AS 'zAssetAnalyState-Worker Flags',
		zAssetAnalyState.ZWORKERTYPE AS 'zAssetAnalyState-Worker Type',
		DateTime(zAssetAnalyState.ZIGNOREUNTILDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Ignore Until Date',
		DateTime(zAssetAnalyState.ZLASTIGNOREDDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Last Ignored Date',
		DateTime(zAssetAnalyState.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Sort Token',
		zMedAnlyAstAttr.ZCHARACTERRECOGNITIONATTRIBUTES AS 'zMedAnlyAstAttr-Character Recognition Attr',
		zCharRecogAttr.ZALGORITHMVERSION AS 'zCharRecogAttr-Algorithm Version',
		zCharRecogAttr.ZADJUSTMENTVERSION AS 'zCharRecogAttr-Adjustment Version',
		zMedAnlyAstAttr.ZVISUALSEARCHATTRIBUTES AS 'zMedAnlyAstAttr-Visual Search Attributes',
		zVisualSearchAttr.ZALGORITHMVERSION AS 'zVisualSearchAttr-Algorithm Version',
		zVisualSearchAttr.ZADJUSTMENTVERSION AS 'zVisualSearchAttr-Adjustment Version',
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
		zUserFeedback.ZUUID AS 'zUserFeedback-UUID-4TableStart',
		zUserFeedback.ZFEATURE AS 'zUserFeedback-Feature',
		zUserFeedback.ZTYPE AS 'zUserFeedback-Type',
		zUserFeedback.ZLASTMODIFIEDDATE AS 'zUserFeedback-Last Modified Date',
		zUserFeedback.ZCONTEXT AS 'zUserFeedback-Context',
		zUserFeedback.ZCLOUDLOCALSTATE AS 'zUserFeedback-Cloud Local State',
		zUserFeedback.ZCLOUDDELETESTATE AS 'zUserFeedback-Cloud Delete State',
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
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		zAsset.ZPHOTOANALYSISATTRIBUTES AS 'zAsset-Photo Analysis Attributes Key',
		zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZMOMENTSHARE AS 'zAsset-Moment Share Key= zShare-zPK',
		zAsset.ZMOMENT AS 'zAsset-zMoment Key= zMoment-zPK',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZHIGHLIGHTBEINGASSETS AS 'zAsset-Highlight Being Assets-HBA Key',
		zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Highlight Being Extended Assets-HBEA Key',
		zAsset.ZHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Highlight Being Key Asset Private-HBKAP Key',
		zAsset.ZHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Highlight Being Key Asset Shared-HBKAS Key',
		zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Highligh Being Summary Assets-HBSA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS AS 'zAsset-Day Group Highlight Being Assets-DGHBA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Day Group Highlight Being Key Asset Private-DGHBKAP Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Day Group Highlight Being Key Asset Shared-DGHBKAS Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key',
		zAsset.ZMONTHHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Month Highlight Being Key Asset Private-MHBKAP Key',
		zAsset.ZMONTHHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Month Highlight Being Key Asset Shared-MHBKAS Key',
		zAsset.ZYEARHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Year Highlight Being Key Asset Private-YHBKAP Key',
		zAsset.ZYEARHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Year Highlight Being Key Asset Shared-YHBKAS Key',
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
		zAssetContrib.Z_PK AS 'zAsstContrib-zPK',
		zAssetContrib.Z_ENT AS 'zAsstContrib-zEnt',
		zAssetContrib.Z_OPT AS 'zAsstContrib-zOpt',
		zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS AS 'zAsstContrib-3Library Scope Asset Contributors= zAssset-zPK',
		zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
		zAssetDes.Z_PK AS 'zAssetDes-zPK',
		zAssetDes.Z_ENT AS 'zAssetDes-zENT',
		zAssetDes.Z_OPT AS 'zAssetDes-zOPT',
		zAssetDes.ZASSETATTRIBUTES AS 'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK',
		zCharRecogAttr.Z_PK AS 'zCharRecogAttr-zPK',
		zCharRecogAttr.Z_ENT AS 'zCharRecogAttr-zENT',
		zCharRecogAttr.Z_OPT AS 'zCharRecogAttr-zOPT',
		zCharRecogAttr.ZMEDIAANALYSISASSETATTRIBUTES AS 'zCharRecogAttr-MedAssetAttr= zMedAnlyAstAttr-zPK',
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
		zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
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
		zGenAlbum.ZSYNDICATE AS 'zGenAlbum-zSyndicate',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
		SWYConverszGenAlbum.ZUUID AS 'SWYConverszGenAlbum-UUID',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud_GUID = store.cloudphotodb',
		SWYConverszGenAlbum.ZCLOUDGUID AS 'SWYConverszGenAlbum-Cloud GUID',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',
		SWYConverszGenAlbum.ZPROJECTRENDERUUID AS 'SWYConverszGenAlbum-Project Render UUID',
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
		zMemory.Z_PK AS 'zMemory-zPK',
		zMemory.Z_ENT AS 'zMemory-zENT',
		zMemory.Z_OPT AS 'zMemory-zOPT',
		zMemory.ZKEYASSET AS 'zMemory-Key Asset= zAsset-zPK',
		zMemory.ZUUID AS 'zMemory-UUID',
		zMoment.Z_PK AS 'zMoment-zPK',
		zMoment.Z_ENT AS 'zMoment-zENT',
		zMoment.Z_OPT AS 'zMoment-zOPT',
		zMoment.ZHIGHLIGHT AS 'zMoment-Highlight Key',
		zMoment.ZUUID AS 'zMoment-UUID',
		zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
		zPerson.Z_ENT AS 'zPerson-zEnt',
		zPerson.Z_OPT AS 'zPerson-zOpt',
		zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',
		zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
		zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
		zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
		zPhotoAnalysisAssetAttr.Z_PK AS 'zPhotoAnalysisAssetAttr-zPK',
		zPhotoAnalysisAssetAttr.Z_ENT AS 'zPhotoAnalysisAssetAttr-zEnt',
		zPhotoAnalysisAssetAttr.Z_OPT AS 'zPhotoAnalysisAssetAttr-zOpt',
		zPhotoAnalysisAssetAttr.ZASSET AS 'zPhotoAnalysisAssetAttr-zAsset = zAsset-zPK',
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
		zSharePartic.ZPERSON AS 'zSharePartic-Person= zPerson-zPK',
		zSharePartic.ZUUID AS 'zSharePartic-UUID',
		SBKAzSugg.Z_PK AS 'SBKAzSugg-zPK',
		SBKAzSugg.Z_ENT AS 'SBKAzSugg-zENT',
		SBKAzSugg.Z_OPT AS 'SBKAzSugg-zOPT',
		SBKAzSugg.ZUUID AS 'SBKAzSugg-UUID',
		SBRAzSugg.Z_PK AS 'SBRAzSugg-zPK',
		SBRAzSugg.Z_ENT AS 'SBRAzSugg-zENT',
		SBRAzSugg.Z_OPT AS 'SBRAzSugg-zOPT',
		SBRAzSugg.ZUUID AS 'SBRAzSugg-UUID',
		z3SuggBRA.Z_3REPRESENTATIVEASSETS1 AS 'z3SuggBRA-3RepAssets1',
		z3SuggBRA.Z_58SUGGESTIONSBEINGREPRESENTATIVEASSETS AS 'z3SuggBRA-58SuggBeingRepAssets',
		z3SuggBKA.Z_58SUGGESTIONSBEINGKEYASSETS AS 'z3SuggBKA-58SuggBeingKeyAssets= zSugg-zPK',
		z3SuggBKA.Z_3KEYASSETS AS 'z3SuggBKA-3KeyAssets= zAsset-zPK',
		zUnmAdj.Z_PK AS 'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key',
		zUnmAdj.Z_OPT AS 'zUnmAdj-zOPT',
		zUnmAdj.Z_ENT AS 'zUnmAdj-zENT',
		zUnmAdj.ZASSETATTRIBUTES AS 'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK',
		zUnmAdj.ZUUID AS 'zUnmAdj-UUID',
		zUnmAdj.ZOTHERADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Other Adjustments Fingerprint',
		zUnmAdj.ZSIMILARTOORIGINALADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Similar to Orig Adjustments Fingerprint',
		zUserFeedback.Z_PK AS 'zUserFeedback-zPK',
		zUserFeedback.Z_ENT AS 'zUserFeedback-zENT',
		zUserFeedback.Z_OPT AS 'zUserFeedback-zOPT',
		zUserFeedback.ZPERSON AS 'zUserFeedback-Person= zPerson-zPK',
		zUserFeedback.ZMEMORY AS 'zUserFeedback-Memory= zMemory-zPK',
		zUserFeedback.ZUUID AS 'zUserFeedback-UUID',
		zVisualSearchAttr.Z_PK AS 'zVisualSearchAttr-zPK',
		zVisualSearchAttr.Z_ENT AS 'zVisualSearchAttr-zENT',
		zVisualSearchAttr.Z_OPT AS 'zVisualSearchAttr-zOPT',
		zVisualSearchAttr.ZMEDIAANALYSISASSETATTRIBUTES AS 'zVisualSearchAttr-MedAssetAttr= zMedAnlyAstAttr-zPK',
		z27AlbumLists.Z_27ALBUMS AS 'z27AlbumList-27Albums= zGenAlbum-zPK',
		z27AlbumLists.Z_2ALBUMLISTS AS 'z27AlbumList-Album List Key',
		z27AlbumLists.Z_FOK_27ALBUMS AS 'z27AlbumList-FOK27Albums Key',
		z28Assets.Z_28ALBUMS AS 'z28Assets-28Albums= zGenAlbum-zPK',
		z28Assets.Z_3ASSETS AS 'z28Assets-3Asset Key= zAsset-zPK in the Album',
		z28Assets.Z_FOK_3ASSETS AS 'z28Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY',
		z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AS 'z3MemoryBMCAs-3MovieCuratedAssets= zAsset-zPK',
		z3MemoryBCAs.Z_3CURATEDASSETS AS 'z3MemoryBCAs-3CuratedAssets= zAsset-zPK',
		z3MemoryBCAs.Z_44MEMORIESBEINGCURATEDASSETS AS 'z3MemoryBCAs-44MemoriesBeingCuratedAssets= zMemory-zPK',
		z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-3ExtCuratedAssets= zAsset-zPK',
		z3MemoryBECAs.Z_44MEMORIESBEINGEXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-44MemoriesBeingExtCuratedAssets= zMemory-zPK',
		z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AS 'z3MemoryBRAs-3RepresentativeAssets= zAsset-zPK',
		z3MemoryBRAs.Z_44MEMORIESBEINGREPRESENTATIVEASSETS AS 'z3MemoryBRAs-44RepresentativeAssets= zMemory-zPK',
		z3MemoryBUCAs.Z_3USERCURATEDASSETS AS 'z3MemoryBUCAs-3UserCuratedAssets= zAsset-zPK',
		z3MemoryBUCAs.Z_44MEMORIESBEINGUSERCURATEDASSETS AS 'z3MemoryBUCAs-44MemoriesBeingUserCuratedAssets= zMemory-zPK',
		z3MemoryBCUAs.Z_44MEMORIESBEINGCUSTOMUSERASSETS AS 'z3MemoryBCAs-44Memories Being Custom User Assets',
		z3MemoryBCUAs.Z_3CUSTOMUSERASSETS AS 'z3MemoryBCAs-3Custom User Assets',
		z3MemoryBCUAs.Z_FOK_3CUSTOMUSERASSETS AS 'z3MemoryBCAs-FOK-3Custom User Assets'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT
			LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
			LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
			LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
			LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
			LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
			LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
			LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
			LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDRESOURCE zCldRes ON zCldRes.ZCLOUDMASTER = zCldMast.Z_PK
			LEFT JOIN ZASSETANALYSISSTATE zAssetAnalyState ON zAssetAnalyState.ZASSET = zAsset.Z_PK
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
			LEFT JOIN ZPHOTOANALYSISASSETATTRIBUTES zPhotoAnalysisAssetAttr ON zPhotoAnalysisAssetAttr.ZASSET = zAsset.Z_PK
			LEFT JOIN ZCOMPUTEDASSETATTRIBUTES zCompAssetAttr ON zCompAssetAttr.Z_PK = zAsset.ZCOMPUTEDATTRIBUTES
			LEFT JOIN ZCHARACTERRECOGNITIONATTRIBUTES zCharRecogAttr ON zCharRecogAttr.Z_PK = zMedAnlyAstAttr.ZCHARACTERRECOGNITIONATTRIBUTES
			LEFT JOIN ZVISUALSEARCHATTRIBUTES zVisualSearchAttr ON zVisualSearchAttr.Z_PK = zMedAnlyAstAttr.ZVISUALSEARCHATTRIBUTES
			LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
			LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
			LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
			LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.ZSHARE = SPLzShare.Z_PK
			LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
			LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
			LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
			LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
			LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
			LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
			LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
			LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
			LEFT JOIN Z_3MEMORIESBEINGCURATEDASSETS z3MemoryBCAs ON zAsset.Z_PK = z3MemoryBCAs.Z_3CURATEDASSETS
			LEFT JOIN ZMEMORY zMemory ON z3MemoryBCAs.Z_44MEMORIESBEINGCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGCUSTOMUSERASSETS z3MemoryBCUAs ON zAsset.Z_PK = z3MemoryBCUAs.Z_3CUSTOMUSERASSETS AND z3MemoryBCUAs.Z_44MEMORIESBEINGCUSTOMUSERASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGEXTENDEDCURATEDASSETS z3MemoryBECAs ON zAsset.Z_PK = z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AND z3MemoryBECAs.Z_44MEMORIESBEINGEXTENDEDCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGMOVIECURATEDASSETS z3MemoryBMCAs ON zAsset.Z_PK = z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AND z3MemoryBMCAs.Z_44MEMORIESBEINGMOVIECURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGREPRESENTATIVEASSETS z3MemoryBRAs ON zAsset.Z_PK = z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AND z3MemoryBRAs.Z_44MEMORIESBEINGREPRESENTATIVEASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGUSERCURATEDASSETS z3MemoryBUCAs ON zAsset.Z_PK = z3MemoryBUCAs.Z_3USERCURATEDASSETS AND z3MemoryBUCAs.Z_44MEMORIESBEINGUSERCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN ZUSERFEEDBACK zUserFeedback ON zUserFeedback.ZMEMORY = zMemory.Z_PK
			LEFT JOIN ZMOMENT zMoment ON zMoment.Z_PK = zAsset.ZMOMENT
			LEFT JOIN Z_3SUGGESTIONSBEINGKEYASSETS z3SuggBKA ON z3SuggBKA.Z_3KEYASSETS = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBKAzSugg ON SBKAzSugg.Z_PK = z3SuggBKA.Z_58SUGGESTIONSBEINGKEYASSETS
			LEFT JOIN Z_3SUGGESTIONSBEINGREPRESENTATIVEASSETS z3SuggBRA ON z3SuggBRA.Z_3REPRESENTATIVEASSETS1 = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBRAzSugg ON SBRAzSugg.Z_PK = z3SuggBRA.Z_58SUGGESTIONSBEINGREPRESENTATIVEASSETS
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
							row[1080], row[1081], row[1082]))

		data_headers = (('zAsset-Added Date-0', 'datetime'),
						'zAsset- SortToken -CameraRoll-1',
						'zAsset Complete-2',
						'zAsset-zPK-4QueryStart-3',
						'zAddAssetAttr-zPK-4QueryStart-4',
						'zAsset-UUID = store.cloudphotodb-4QueryStart-5',
						'zAddAssetAttr-Master Fingerprint-4TableStart-6',
						'zIntResou-Fingerprint-4TableStart-7',
						'zAsset-Bundle Scope-8',
						'zAsset-Syndication State-9',
						'zAsset-Cloud is My Asset-10',
						'zAsset-Cloud is deletable-Asset-11',
						'zAsset-Cloud_Local_State-12',
						'zAsset-Visibility State-13',
						'zExtAttr-Camera Make-14',
						'zExtAttr-Camera Model-15',
						'zExtAttr-Lens Model-16',
						'zExtAttr-Flash Fired-17',
						'zExtAttr-Focal Lenght-18',
						'zExtAttr-Focal Lenth in 35MM-19',
						'zExtAttr-Digital Zoom Ratio-20',
						'zAsset-Derived Camera Capture Device-21',
						'zAddAssetAttr-Camera Captured Device-22',
						'zAddAssetAttr-Imported by-23',
						'zCldMast-Imported By-24',
						'zAddAssetAttr.Imported by Bundle Identifier-25',
						'zAddAssetAttr-Imported By Display Name-26',
						'zCldMast-Imported by Bundle ID-27',
						'zCldMast-Imported by Display Name-28',
						'zAsset-Saved Asset Type-29',
						'zAsset-Directory-Path-30',
						'zAsset-Filename-31',
						'zAddAssetAttr- Original Filename-32',
						'zCldMast- Original Filename-33',
						'zAddAssetAttr- Syndication Identifier-SWY-Files-34',
						'zAsset-Active Library Scope Participation State -4QueryStart-35',
						'zAsset-Library Scope Share State- StillTesting -4QueryStart-36',
						'zShare-Cloud Photo Count-SPL -4QueryStart-37',
						'zShare-Cloud Video Count-SPL -4QueryStart-38',
						('zAddAssetAttr-Date Created Source-39', 'datetime'),
						('zAsset-Date Created-40', 'datetime'),
						('zCldMast-Creation Date-41', 'datetime'),
						('zIntResou-CldMst Date Created-42', 'datetime'),
						'zAddAssetAttr-Time Zone Name-43',
						'zAddAssetAttr-Time Zone Offset-44',
						'zAddAssetAttr-Inferred Time Zone Offset-45',
						'zAddAssetAttr-EXIF-String-46',
						('zAsset-Modification Date-47', 'datetime'),
						('zAsset-Last Shared Date-48', 'datetime'),
						'zCldMast-Cloud Local State-49',
						('zCldMast-Import Date-50', 'datetime'),
						('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-51', 'datetime'),
						'zAddAssetAttr-Import Session ID-4QueryStart-52',
						('zAddAssetAttr-Alt Import Image Date-53', 'datetime'),
						'zCldMast-Import Session ID- AirDrop-StillTesting- 4QueryStart-54',
						('zAsset-Cloud Batch Publish Date-55', 'datetime'),
						('zAsset-Cloud Server Publish Date-56', 'datetime'),
						'zAsset-Cloud Download Requests-57',
						'zAsset-Cloud Batch ID-58',
						'zAddAssetAttr-Upload Attempts-59',
						'zAsset-Latitude-60',
						'zExtAttr-Latitude-61',
						'zAsset-Longitude-62',
						'zExtAttr-Longitude-63',
						'zAddAssetAttr-GPS Horizontal Accuracy-64',
						'zAddAssetAttr-Location Hash-65',
						'zAddAssetAttr-Shifted Location Valid-66',
						'zAddAssetAttr-Shifted Location Data-67',
						'zAddAssetAttr-Reverse Location Is Valid-68',
						'zAddAssetAttr-Reverse Location Data-69',
						'ParentzGenAlbum-UUID-4QueryStart-70',
						'zGenAlbum-UUID-4QueryStart-71',
						'SWYConverszGenAlbum-UUID-4QueryStart-72',
						'ParentzGenAlbum-Cloud GUID-4QueryStart-73',
						'zGenAlbum-Cloud GUID-4QueryStart-74',
						'SWYConverszGenAlbum-Cloud GUID-4QueryStart-75',
						'zCldShareAlbumInvRec-Album GUID-4QueryStart-76',
						'zCldShareAlbumInvRec-Cloud GUID-4QueryStart-77',
						'zGenAlbum-Project Render UUID-4QueryStart-78',
						'SWYConverszGenAlbum-Project Render UUID-4QueryStart-79',
						'ParentzGenAlbum-Cloud-Local-State-4QueryStart-80',
						'zGenAlbum-Cloud_Local_State-4QueryStart-81',
						'SWYConverszGenAlbum-Cloud_Local_State-4QueryStart-82',
						('ParentzGenAlbum- Creation Date- 4QueryStart-83', 'datetime'),
						('zGenAlbum- Creation Date- 4QueryStart-84', 'datetime'),
						('SWYConverszGenAlbum- Creation Date- 4QueryStart-85', 'datetime'),
						('zGenAlbum- Cloud Creation Date- 4QueryStart-86', 'datetime'),
						('SWYConverszGenAlbum- Cloud Creation Date- 4QueryStart-87', 'datetime'),
						('zGenAlbum- Start Date- 4QueryStart-88', 'datetime'),
						('SWYConverszGenAlbum- Start Date- 4QueryStart-89', 'datetime'),
						('zGenAlbum- End Date- 4QueryStart-90', 'datetime'),
						('SWYConverszGenAlbum- End Date- 4QueryStart-91', 'datetime'),
						('zGenAlbum-Cloud Subscription Date- 4QueryStart-92', 'datetime'),
						('SWYConverszGenAlbum-Cloud Subscription Date- 4QueryStart-93', 'datetime'),
						'ParentzGenAlbum- Title- 4QueryStart-94',
						'zGenAlbum- Title-User&System Applied- 4QueryStart-95',
						'SWYConverszGenAlbum- Title -User&System Applied- 4QueryStart-96',
						'zGenAlbum-Import Session ID-SWY- 4QueryStart-97',
						'zAsset- Conversation= zGenAlbum_zPK -4QueryStart-98',
						'SWYConverszGenAlbum- Import Session ID-SWY- 4QueryStart-99',
						'zGenAlbum-Imported by Bundle Identifier- 4QueryStart-100',
						'SWYzGenAlbum-Imported by Bundle Identifier- 4QueryStart-101',
						'SWYConverszGenAlbum- Syndicate-4QueryStart-102',
						'zGenAlbum-zENT- Entity- 4QueryStart-103',
						'ParentzGenAlbum- Kind- 4QueryStart-104',
						'zGenAlbum-Album Kind- 4QueryStart-105',
						'SWYConverszGenAlbum-Album Kind- 4QueryStart-106',
						'AAAzCldMastMedData-zOPT-107',
						'zAddAssetAttr-Media Metadata Type-108',
						'AAAzCldMastMedData-Data-109',
						'CldMasterzCldMastMedData-zOPT-110',
						'zCldMast-Media Metadata Type-111',
						'CMzCldMastMedData-Data-112',
						'zAsset-Search Index Rebuild State-113',
						'zAddAssetAttr-Syndication History-114',
						'zMedAnlyAstAttr-Syndication Processing Version-115',
						'zMedAnlyAstAttr-Syndication Processing Value-116',
						'zAsset-Orientation-117',
						'zAddAssetAttr-Original Orientation-118',
						'zAsset-Kind-119',
						'zAsset-Kind-Sub-Type-120',
						'zAddAssetAttr-Cloud Kind Sub Type-121',
						'zAsset-Playback Style-122',
						'zAsset-Playback Variation-123',
						'zAsset-Video Duration-124',
						'zExtAttr-Duration-125',
						'zAsset-Video CP Duration-126',
						'zAddAssetAttr-Video CP Duration Time Scale-127',
						'zAsset-Video CP Visibility State-128',
						'zAddAssetAttr-Video CP Display Value-129',
						'zAddAssetAttr-Video CP Display Time Scale-130',
						'zIntResou-Datastore Class ID-131',
						'zAsset-Cloud Placeholder Kind-132',
						'zIntResou-Local Availability-133',
						'zIntResou-Local Availability Target-134',
						'zIntResou-Cloud Local State-135',
						'zIntResou-Remote Availability-136',
						'zIntResou-Remote Availability Target-137',
						'zIntResou-Transient Cloud Master-138',
						'zIntResou-Side Car Index-139',
						'zIntResou- File ID-140',
						'zIntResou-Version-141',
						'zAddAssetAttr- Original-File-Size-142',
						'zIntResou-Resource Type-143',
						'zIntResou-Datastore Sub-Type-144',
						'zIntResou-Cloud Source Type-145',
						'zIntResou-Data Length-146',
						'zIntResou-Recipe ID-147',
						('zIntResou-Cloud Last Prefetch Date-148', 'datetime'),
						'zIntResou-Cloud Prefetch Count-149',
						('zIntResou- Cloud-Last-OnDemand Download-Date-150', 'datetime'),
						'zIntResou-UniformTypeID_UTI_Conformance_Hint-151',
						'zIntResou-Compact-UTI-152',
						'zAsset-Uniform Type ID-153',
						'zAsset-Original Color Space-154',
						'zCldMast-Uniform_Type_ID-155',
						'zCldMast-Full Size JPEG Source-156',
						'zAsset-HDR Gain-157',
						'zAsset-zHDR_Type-158',
						'zExtAttr-Codec-159',
						'zIntResou-Codec Four Char Code Name-160',
						'zCldMast-Codec Name-161',
						'zCldMast-Video Frame Rate-162',
						'zCldMast-Placeholder State-163',
						'zAsset-Depth_Type-164',
						'zAsset-Avalanche UUID-4TableStart-165',
						'zAsset-Avalanche_Pick_Type-BurstAsset-166',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-167',
						'zAddAssetAttr-Cloud Recovery State-168',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-169',
						'zAsset-Deferred Processing Needed-170',
						'zAsset-Video Deferred Processing Needed-171',
						'zAddAssetAttr-Deferred Photo Identifier-4QueryStart-172',
						'zAddAssetAttr-Deferred Processing Candidate Options-173',
						'zAsset-Has Adjustments-Camera-Effects-Filters-174',
						'zUnmAdj-UUID-4TableStart-175',
						'zAsset-Adjustment Timestamp-176',
						'zUnmAdj-Adjustment Timestamp-177',
						'zAddAssetAttr-Editor Bundle ID-178',
						'zUnmAdj-Editor Localized Name-179',
						'zUnmAdj-Adjustment Format ID-180',
						'zAddAssetAttr-Montage-181',
						'zUnmAdj-Adjustment Render Types-182',
						'zUnmAdj-Adjustment Format Version-183',
						'zUnmAdj-Adjustment Base Image Format-184',
						'zAsset-Favorite-185',
						'zAsset-Hidden-186',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-187',
						('zAsset-Trashed Date-188', 'datetime'),
						'zAsset-Trashed by Participant= zSharePartic_zPK-4QueryStart-189',
						'zAsset-Delete-Reason-190',
						'zIntResou-Trash State-191',
						('zIntResou-Trashed Date-192', 'datetime'),
						'zAsset-Cloud Delete State-193',
						'zIntResou-Cloud Delete State-194',
						'zAddAssetAttr-PTP Trashed State-195',
						'zIntResou-PTP Trashed State-196',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-4TableStart-197',
						'zMedAnlyAstAttr-Media Analysis Timestamp-198',
						('zAsset-Analysis State Modification Date-199', 'datetime'),
						'zAddAssetAttr- Pending View Count-200',
						'zAddAssetAttr- View Count-201',
						'zAddAssetAttr- Pending Play Count-202',
						'zAddAssetAttr- Play Count-203',
						'zAddAssetAttr- Pending Share Count-204',
						'zAddAssetAttr- Share Count-205',
						'zAddAssetAttr-Allowed for Analysis-206',
						'zAddAssetAttr-Scene Analysis Version-207',
						'zAddAssetAttr-Scene Analysis is From Preview-208',
						'zAddAssetAttr-Scene Analysis Timestamp-209',
						'zAsset-Duplication Asset Visibility State-210',
						'zAddAssetAttr-Destination Asset Copy State-211',
						'zAddAssetAttr-Duplicate Detector Perceptual Processing State-212',
						'zAddAssetAttr-Source Asset for Duplication Scope ID-213',
						'zCldMast-Source Master For Duplication Scope ID-214',
						'zAddAssetAttr-Source Asset For Duplication ID-215',
						'zCldMast-Source Master for Duplication ID-216',
						'zAddAssetAttr-Variation Suggestions States-217',
						'zAsset-High Frame Rate State-218',
						'zAsset-Video Key Frame Time Scale-219',
						'zAsset-Video Key Frame Value-220',
						'zExtAttr-ISO-221',
						'zExtAttr-Metering Mode-222',
						'zExtAttr-Sample Rate-223',
						'zExtAttr-Track Format-224',
						'zExtAttr-White Balance-225',
						'zExtAttr-Aperture-226',
						'zExtAttr-BitRate-227',
						'zExtAttr-Exposure Bias-228',
						'zExtAttr-Frames Per Second-229',
						'zExtAttr-Shutter Speed-230',
						'zExtAttr-Slush Scene Bias-231',
						'zExtAttr-Slush Version-232',
						'zExtAttr-Slush Preset-233',
						'zExtAttr-Slush Warm Bias-234',
						'zAsset-Height-235',
						'zAddAssetAttr-Original Height-236',
						'zIntResou-Unoriented Height-237',
						'zAsset-Width-238',
						'zAddAssetAttr-Original Width-239',
						'zIntResou-Unoriented Width-240',
						'zShare-Thumbnail Image Data-241',
						'SPLzShare-Thumbnail Image Data-242',
						'zAsset-Thumbnail Index-243',
						'zAddAssetAttr-Embedded Thumbnail Height-244',
						'zAddAssetAttr-Embedded Thumbnail Length-245',
						'zAddAssetAttr-Embedded Thumbnail Offset-246',
						'zAddAssetAttr-Embedded Thumbnail Width-247',
						'zAsset-Packed Acceptable Crop Rect-248',
						'zAsset-Packed Badge Attributes-249',
						'zAsset-Packed Preferred Crop Rect-250',
						'zAsset-Curation Score-251',
						'zAsset-Camera Processing Adjustment State-252',
						'zAsset-Depth Type-253',
						'zAsset-Is Magic Carpet-QuicktimeMOVfile-254',
						'zAddAssetAttr-Orig Resource Choice-255',
						'zAddAssetAttr-Spatial Over Capture Group ID-256',
						'zAddAssetAttr-Place Annotation Data-257',
						'zAddAssetAttr-Distance Identity-258',
						'zAddAssetAttr-Edited IPTC Attributes-259',
						'zAssetDes-Long Description-260',
						'zAddAssetAttr-Asset Description-261',
						'zAddAssetAttr-Title-Comments via Cloud Website-262',
						'zAddAssetAttr-Accessibility Description-263',
						'zAddAssetAttr-Photo Stream Tag ID-264',
						'zPhotoAnalysisAssetAttr-Wallpaper Properties Version-265',
						'zPhotoAnalysisAssetAttr-Wallpaper Properties Timestamp-266',
						('zCldFeedEnt-Entry Date-267', 'datetime'),
						'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-268',
						'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-269',
						'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-270',
						'zCldFeedEnt-Entry Priority Number-271',
						'zCldFeedEnt-Entry Type Number-272',
						'zCldSharedComment-Cloud GUID-4TableStart-273',
						('zCldSharedComment-Date-274', 'datetime'),
						('zCldSharedComment-Comment Client Date-275', 'datetime'),
						('zAsset-Cloud Last Viewed Comment Date-276', 'datetime'),
						'zCldSharedComment-Type-277',
						'zCldSharedComment-Comment Text-278',
						'zCldSharedComment-Commenter Hashed Person ID-279',
						'zCldSharedComment-Batch Comment-280',
						'zCldSharedComment-Is a Caption-281',
						'zAsset-Cloud Has Comments by Me-282',
						'zCldSharedComment-Is My Comment-283',
						'zCldSharedComment-Is Deletable-284',
						'zAsset-Cloud Has Comments Conversation-285',
						'zAsset-Cloud Has Unseen Comments-286',
						'zCldSharedComment-Liked-287',
						'zAddAssetAttr-Share Type-288',
						'zAsset-Library Scope Share State- StillTesting-289',
						'zAsset-Active Library Scope Participation State-290',
						'zAddAssetAttr-Library Scope Asset Contributors To Update-291',
						'zShare-UUID-CMM-4TableStart-292',
						'SPLzShare-UUID-SPL-4TableStart-293',
						'zShare-zENT-CMM-294',
						'SPLzShare-zENT-SPL-295',
						'zSharePartic-z54SHARE-296',
						'SPLzSharePartic-z54SHARE-297',
						'zShare-Status-CMM-298',
						'SPLzShare-Status-SPL-299',
						'zShare-Scope Type-CMM-300',
						'SPLzShare-Scope Type-SPL-301',
						'zShare-Local Publish State-CMM-302',
						'SPLzShare-Local Publish State-SPL-303',
						'zShare-Public Permission-CMM-304',
						'SPLzShare-Public Permission-SPL-305',
						'zShare-Originating Scope ID-CMM-306',
						'SPLzShare-Originating Scope ID-SPL-307',
						'zShare-Scope ID-CMM-308',
						'SPLzShare-Scope ID-SPL-309',
						'zShare-Title-CMM-310',
						'SPLzShare-Title-SPL-311',
						'zShare-Share URL-CMM-312',
						'SPLzShare-Share URL-SPL-313',
						('zShare-Creation Date-CMM-314', 'datetime'),
						('SPLzShare-Creation Date-SPL-315', 'datetime'),
						('zShare-Start Date-CMM-316', 'datetime'),
						('SPLzShare-Start Date-SPL-317', 'datetime'),
						('zShare-End Date-CMM-318', 'datetime'),
						('SPLzShare-End Date-SPL-319', 'datetime'),
						('zShare-Expiry Date-CMM-320', 'datetime'),
						('SPLzShare-Expiry Date-SPL-321', 'datetime'),
						'zShare-Cloud Item Count-CMM-322',
						'SPLzShare-Cloud Item Count-SPL-323',
						'zShare-Asset Count-CMM-324',
						'SPLzShare-Asset Count-SPL-325',
						'zShare-Cloud Photo Count-CMM-326',
						'SPLzShare-Cloud Photo Count-SPL-327',
						'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-CMM-328',
						'SPLzShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-SPL-329',
						'zShare-Photos Count-CMM-330',
						'SPLzShare-Photos Count-CMM-SPL-331',
						'zShare-Uploaded Photos Count-CMM-332',
						'SPLzShare-Uploaded Photos Count-SPL-333',
						'zShare-Cloud Video Count-CMM-334',
						'SPLzShare-Cloud Video Count-SPL-335',
						'zShare-Videos Count-CMM-336',
						'SPLzShare-Videos Count-SPL-337',
						'zShare-Uploaded Videos Count-CMM-338',
						'SPLzShare-Uploaded Videos Count-SPL-339',
						'zShare-Force Sync Attempted-CMM-340',
						'SPLzShare-Force Sync Attempted-SPL-341',
						'zShare-Cloud Local State-CMM-342',
						'SPLzShare-Cloud Local State-SPL-343',
						'zShare-Scope Syncing State-CMM-344',
						'SPLzShare-Scope Syncing State-SPL-345',
						'zShare-Auto Share Policy-CMM-346',
						'SPLzShare-Auto Share Policy-SPL-347',
						'zShare-Should Notify On Upload Completion-CMM-348',
						'SPLzShare-Should Notify On Upload Completion-SPL-349',
						'zAsset-Trashed by Participant= zSharePartic_zPK-SPL-CMM-350',
						'zShare-Trashed State-CMM-351',
						'SPLzShare-Trashed State-SPL-352',
						'zShare-Cloud Delete State-CMM-353',
						'SPLzShare-Cloud Delete State-SPL-354',
						('zShare-Trashed Date-CMM-355', 'datetime'),
						('SPLzShare-Trashed Date-SPL-356', 'datetime'),
						('zShare-LastParticipant Asset Trash Notification Date-CMM-357', 'datetime'),
						('SPLzShare-LastParticipant Asset Trash Notification Date-SPL-358', 'datetime'),
						('zShare-Last Participant Asset Trash Notification View Date-CMM-359', 'datetime'),
						('SPLzShare-Last Participant Asset Trash Notification View Date-SPL-360', 'datetime'),
						'zShare-Exit Source-CMM-361',
						'SPLzShare-Exit Source-SPL-362',
						'zShare-SPL_Exit State-CMM-363',
						'SPLzShare-SPL_Exit State-SPL-364',
						'zShare-Exit Type-CMM-365',
						'SPLzShare-Exit Type-SPL-366',
						'zShare-Should Ignor Budgets-CMM-367',
						'SPLzShare-Should Ignor Budgets-SPL-368',
						'zShare-Preview State-CMM-369',
						'SPLzShare-Preview State-SPL-370',
						'zShare-Preview Data-CMM-371',
						'SPLzShare-Preview Data-SPL-372',
						'zShare-Rules-CMM-373',
						'SPLzShare-Rules-SPL-374',
						'zShare-Thumbnail Image Data-CMM-375',
						'SPLzShare-Thumbnail Image Data-SPL-376',
						'zShare-Participant Cloud Update State-CMM-377',
						'SPLzShare-Participant Cloud Update State-SPL-378',
						'zSharePartic-UUID-4TableStart-379',
						'SPLzSharePartic-UUID-4TableStart-380',
						'zSharePartic-Acceptance Status-381',
						'SPLzSharePartic-Acceptance Status-382',
						'zSharePartic-Is Current User-383',
						'SPLzSharePartic-Is Current User-384',
						'zSharePartic-Role-385',
						'SPLzSharePartic-Role-386',
						'zSharePartic-Premission-387',
						'SPLzSharePartic-Premission-388',
						'zSharePartic-Participant ID-389',
						'SPLzSharePartic-Participant ID-390',
						'zSharePartic-User ID-391',
						'SPLzSharePartic-User ID-392',
						'zAsstContrib-Participant= zSharePartic-zPK-4TableStart-393',
						'SPLzSharePartic-zPK-4TableStart-394',
						'zSharePartic-zPK-4TableStart-395',
						'zSharePartic-Email Address-396',
						'SPLzSharePartic-Email Address-397',
						'zSharePartic-Phone Number-398',
						'SPLzSharePartic-Phone Number-399',
						'zSharePartic-Exit State-400',
						'SPLzSharePartic-Exit State-401',
						'ParentzGenAlbum-UUID-4TableStart-402',
						'zGenAlbum-UUID-4TableStart-403',
						'SWYConverszGenAlbum-UUID-4TableStart-404',
						'ParentzGenAlbum-Cloud GUID-4TableStart-405',
						'zGenAlbum-Cloud GUID-4TableStart-406',
						'SWYConverszGenAlbum-Cloud GUID-4TableStart-407',
						'zCldShareAlbumInvRec-Album GUID-4TableStart-408',
						'zCldShareAlbumInvRec-Cloud GUID-4TableStart-409',
						'zGenAlbum-Project Render UUID-4TableStart-410',
						'SWYConverszGenAlbum-Project Render UUID-4TableStart-411',
						'zAlbumList-Needs Reordering Number-412',
						'zGenAlbum-zENT- Entity-413',
						'ParentzGenAlbum-Kind-414',
						'zGenAlbum-Album Kind-415',
						'SWYConverszGenAlbum-Album Kind-416',
						'ParentzGenAlbum-Cloud-Local-State-417',
						'zGenAlbum-Cloud_Local_State-418',
						'SWYConverszGenAlbum-Cloud_Local_State-419',
						'ParentzGenAlbum- Title-420',
						'zGenAlbum- Title-User&System Applied-421',
						'SWYConverszGenAlbum- Title -User&System Applied-422',
						'zGenAlbum-Import Session ID-SWY-423',
						'zAsset- Conversation= zGenAlbum_zPK-424',
						'SWYConverszGenAlbum- Import Session ID-SWY-425',
						'zGenAlbum-Imported by Bundle Identifier-426',
						'SWYzGenAlbum-Imported by Bundle Identifier-427',
						'SWYConverszGenAlbum- Syndicate-428',
						('ParentzGenAlbum-Creation Date-429', 'datetime'),
						('zGenAlbum-Creation Date-430', 'datetime'),
						('SWYConverszGenAlbum-Creation Date-431', 'datetime'),
						('zGenAlbum-Cloud Creation Date-432', 'datetime'),
						('SWYConverszGenAlbum-Cloud Creation Date-433', 'datetime'),
						('zGenAlbum-Start Date-434', 'datetime'),
						('SWYConverszGenAlbum-Start Date-435', 'datetime'),
						('zGenAlbum-End Date-436', 'datetime'),
						('SWYConverszGenAlbum-End Date-437', 'datetime'),
						('zGenAlbum-Cloud Subscription Date-438', 'datetime'),
						('SWYConverszGenAlbum-Cloud Subscription Date-439', 'datetime'),
						'ParentzGenAlbum-Pending Items Count-440',
						'zGenAlbum-Pending Items Count-441',
						'SWYConverszGenAlbum-Pending Items Count-442',
						'ParentzGenAlbum-Pending Items Type-443',
						'zGenAlbum-Pending Items Type-444',
						'SWYConverszGenAlbum-Pending Items Type-445',
						'zGenAlbum- Cached Photos Count-446',
						'SWYConverszGenAlbum- Cached Photos Count-447',
						'zGenAlbum- Cached Videos Count-448',
						'SWYConverszGenAlbum- Cached Videos Count-449',
						'zGenAlbum- Cached Count-450',
						'SWYConverszGenAlbum- Cached Count-451',
						'ParentzGenAlbum-Sync Event Order Key-452',
						'zGenAlbum-Sync Event Order Key-453',
						'SWYConverszGenAlbum-Sync Event Order Key-454',
						'zGenAlbum-Has Unseen Content-455',
						'SWYConverszGenAlbum-Has Unseen Content-456',
						'zGenAlbum-Unseen Asset Count-457',
						'SWYConverszGenAlbum-Unseen Asset Count-458',
						'zGenAlbum-is Owned-459',
						'SWYConverszGenAlbum-is Owned-460',
						'zGenAlbum-Cloud Relationship State-461',
						'SWYConverszGenAlbum-Cloud Relationship State-462',
						'zGenAlbum-Cloud Relationship State Local-463',
						'SWYConverszGenAlbum-Cloud Relationship State Local-464',
						'zGenAlbum-Cloud Owner Mail Key-465',
						'SWYConverszGenAlbum-Cloud Owner Mail Key-466',
						'zGenAlbum-Cloud Owner Frist Name-467',
						'SWYConverszGenAlbum-Cloud Owner Frist Name-468',
						'zGenAlbum-Cloud Owner Last Name-469',
						'SWYConverszGenAlbum-Cloud Owner Last Name-470',
						'zGenAlbum-Cloud Owner Full Name-471',
						'SWYConverszGenAlbum-Cloud Owner Full Name-472',
						'zGenAlbum-Cloud Person ID-473',
						'SWYConverszGenAlbum-Cloud Person ID-474',
						'zAsset-Cloud Owner Hashed Person ID-475',
						'zGenAlbum-Cloud Owner Hashed Person ID-476',
						'SWYConverszGenAlbum-Cloud Owner Hashed Person ID-477',
						'zGenAlbum-Local Cloud Multi-Contributors Enabled-478',
						'SWYConverszGenAlbum-Local Cloud Multi-Contributors Enabled-479',
						'zGenAlbum-Cloud Multi-Contributors Enabled-480',
						'SWYConverszGenAlbum-Cloud Multi-Contributors Enabled-481',
						'zGenAlbum-Cloud Album Sub Type-482',
						'SWYConverszGenAlbum-Cloud Album Sub Type-483',
						('zGenAlbum-Cloud Contribution Date-484', 'datetime'),
						('SWYConverszGenAlbum-Cloud Contribution Date-485', 'datetime'),
						('zGenAlbum-Cloud Last Interesting Change Date-486', 'datetime'),
						('SWYConverszGenAlbum-Cloud Last Interesting Change Date-487', 'datetime'),
						'zGenAlbum-Cloud Notification Enabled-488',
						'SWYConverszGenAlbum-Cloud Notification Enabled-489',
						'ParentzGenAlbum-Pinned-490',
						'zGenAlbum-Pinned-491',
						'SWYConverszGenAlbum-Pinned-492',
						'ParentzGenAlbum-Custom Sort Key-493',
						'zGenAlbum-Custom Sort Key-494',
						'SWYConverszGenAlbum-Custom Sort Key-495',
						'ParentzGenAlbum-Custom Sort Ascending-496',
						'zGenAlbum-Custom Sort Ascending-497',
						'SWYConverszGenAlbum-Custom Sort Ascending-498',
						'ParentzGenAlbum-Is Prototype-499',
						'zGenAlbum-Is Prototype-500',
						'SWYConverszGenAlbum-Is Prototype-501',
						'ParentzGenAlbum-Project Document Type-502',
						'zGenAlbum-Project Document Type-503',
						'SWYConverszGenAlbum-Project Document Type-504',
						'ParentzGenAlbum-Custom Query Type-505',
						'zGenAlbum-Custom Query Type-506',
						'SWYConverszGenAlbum-Custom Query Type-507',
						'ParentzGenAlbum-Trashed State-508',
						('ParentzGenAlbum-Trash Date-509', 'datetime'),
						'zGenAlbum-Trashed State-510',
						('zGenAlbum-Trash Date-511', 'datetime'),
						'SWYConverszGenAlbum-Trashed State-512',
						('SWYConverszGenAlbum-Trash Date-513', 'datetime'),
						'ParentzGenAlbum-Cloud Delete State-514',
						'zGenAlbum-Cloud Delete State-515',
						'SWYConverszGenAlbum-Cloud Delete State-516',
						'zGenAlbum-Cloud Owner Whitelisted-517',
						'SWYConverszGenAlbum-Cloud Owner Whitelisted-518',
						'zGenAlbum-Cloud Local Public URL Enabled-519',
						'SWYConverszGenAlbum-Cloud Local Public URL Enabled-520',
						'zGenAlbum-Cloud Public URL Enabled-521',
						'zGenAlbum-Public URL-522',
						'SWYConverszGenAlbum-Cloud Public URL Enabled-523',
						'SWYConverszGenAlbum-Public URL-524',
						'zGenAlbum-Key Asset Face Thumb Index-525',
						'SWYConverszGenAlbum-Key Asset Face Thumb Index-526',
						'zGenAlbum-Project Text Extension ID-527',
						'SWYConverszGenAlbum-Project Text Extension ID-528',
						'zGenAlbum-User Query Data-529',
						'SWYConverszGenAlbum-User Query Data-530',
						'zGenAlbum-Custom Query Parameters-531',
						'SWYConverszGenAlbum-Custom Query Parameters-532',
						'zGenAlbum-Project Data-533',
						'SWYConverszGenAlbum-Project Data-534',
						'zGenAlbum-Search Index Rebuild State-535',
						'SWYConverszGenAlbum-Search Index Rebuild State-536',
						'zGenAlbum-Duplicate Type-537',
						'SWYConverszGenAlbum-Duplicate Type-538',
						'zGenAlbum-Privacy State-539',
						'SWYConverszGenAlbum-Privacy State-540',
						'zCldShareAlbumInvRec-zUUID-4TableStart-541',
						'zCldShareAlbumInvRec-Is My Invitation to Shared Album-542',
						'zCldShareAlbumInvRec-Invitation State Local-543',
						'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-544',
						('zCldShareAlbumInvRec-Subscription Date-545', 'datetime'),
						'zCldShareAlbumInvRec-Invitee First Name-546',
						'zCldShareAlbumInvRec-Invitee Last Name-547',
						'zCldShareAlbumInvRec-Invitee Full Name-548',
						'zCldShareAlbumInvRec-Invitee Hashed Person ID-549',
						'zCldShareAlbumInvRec-Invitee Email Key-550',
						'zGenAlbum-Key Asset Face ID-551',
						'zFaceCrop-Face Area Points-552',
						'zAsset-Face Adjustment Version-553',
						'zAddAssetAttr-Face Analysis Version-554',
						'zDetFace-Asset Visible-555',
						'zPerson-Face Count-556',
						'zDetFace-Face Crop-557',
						'zDetFace-Face Algorithm Version-558',
						'zDetFace-Adjustment Version-559',
						'zDetFace-UUID-4TableStart-560',
						'zPerson-Person UUID-4TableStart-561',
						'zDetFace-Confirmed Face Crop Generation State-562',
						'zDetFace-Manual-563',
						'zDetFace-Detection Type-564',
						'zPerson-Detection Type-565',
						'zDetFace-VIP Model Type-566',
						'zDetFace-Name Source-567',
						'zDetFace-Cloud Name Source-568',
						'zPerson-Merge Candidate Confidence-569',
						'zPerson-Person URI-570',
						'zPerson-Display Name-571',
						'zPerson-Full Name-572',
						'zPerson-Cloud Verified Type-573',
						'zFaceCrop-State-574',
						'zFaceCrop-Type-575',
						'zFaceCrop-UUID-4TableStart-576',
						'zPerson-Type-577',
						'zPerson-Verified Type-578',
						'zPerson-Gender Type-579',
						'zDetFace-Gender Type-580',
						'zDetFace-Center X-581',
						'zDetFace-Center Y-582',
						'zPerson-Age Type Estimate-583',
						'zDetFace-Age Type Estimate-584',
						'zDetFace-Ethnicity Type-585',
						'zDetFace-Skin Tone Type-586',
						'zDetFace-Hair Type-587',
						'zDetFace-Hair Color Type-588',
						'zDetFace-Head Gear Type-589',
						'zDetFace-Facial Hair Type-590',
						'zDetFace-Has Face Mask-591',
						'zDetFace-Pose Type-592',
						'zDetFace-Face Expression Type-593',
						'zDetFace-Has Smile-594',
						'zDetFace-Smile Type-595',
						'zDetFace-Lip Makeup Type-596',
						'zDetFace-Eyes State-597',
						'zDetFace-Is Left Eye Closed-598',
						'zDetFace-Is Right Eye Closed-599',
						'zDetFace-Gaze Center X-600',
						'zDetFace-Gaze Center Y-601',
						'zDetFace-Face Gaze Type-602',
						'zDetFace-Eye Glasses Type-603',
						'zDetFace-Eye Makeup Type-604',
						'zDetFace-Cluster Squence Number Key-605',
						'zDetFace-Grouping ID-606',
						'zDetFace-Master ID-607',
						'zDetFace-Quality-608',
						'zDetFace-Quality Measure-609',
						'zDetFace-Source Height-610',
						'zDetFace-Source Width-611',
						'zDetFace-Hidden-Asset Hidden-612',
						'zDetFace-In Trash-Recently Deleted-613',
						'zDetFace-Cloud Local State-614',
						'zDetFace-Training Type-615',
						'zDetFace.Pose Yaw-616',
						'zDetFace-Body Center X-617',
						'zDetFace-Body Center Y-618',
						'zDetFace-Body Height-619',
						'zDetFace-Body Width-620',
						'zDetFace-Roll-621',
						'zDetFace-Size-622',
						'zDetFace-Cluster Squence Number-623',
						'zDetFace-Blur Score-624',
						'zDetFacePrint-Face Print Version-625',
						'zMedAnlyAstAttr-Face Count-626',
						'zDetFaceGroup-UUID-4TableStart-627',
						'zDetFaceGroup-Person Builder State-628',
						'zDetFaceGroup-UnNamed Face Count-629',
						'zPerson-In Person Naming Model-630',
						'zPerson-Key Face Pick Source Key-631',
						'zPerson-Manual Order Key-632',
						'zPerson-Question Type-633',
						'zPerson-Suggested For Client Type-634',
						'zPerson-Merge Target Person-635',
						'zPerson-Cloud Local State-636',
						'zFaceCrop-Cloud Local State-637',
						'zFaceCrop-Cloud Type-638',
						'zPerson-Cloud Delete State-639',
						'zFaceCrop-Cloud Delete State-640',
						'zFaceCrop-Invalid Merge Canidate Person UUID-4TableStart-641',
						'zAsset-Highlight Visibility Score-642',
						'zMemory-UUID-4TableStart-643',
						'zMemory-AssetListPredicte-644',
						'zMemory-Score-645',
						'zMemory-SubTitle-646',
						'zMemory-Title-647',
						'zMemory-Category-648',
						'zMemory-SubCategory-649',
						('zMemory-Creation Date-650', 'datetime'),
						('zMemory-Last Enrichment Date-651', 'datetime'),
						'zMemory-User Action Options-652',
						'zMemory-Favorite Memory-653',
						'zMemory-View Count-654',
						'zMemory-Play Count-655',
						'zMemory-Rejected-656',
						'zMemory-Share Count-657',
						'zMemory-Sharing Composition-658',
						('zMemory-Last Movie Play Date-659', 'datetime'),
						('zMemory-Last Viewed Date-660', 'datetime'),
						'zMemory-Pending Play Count Memory-661',
						'zMemory-Pending Share Count Memory-662',
						'zMemory-Pending View Count Memory-663',
						'zMemory-Pending State-664',
						'zMemory-Featured State-665',
						'zMemory-Photos Graph Version-666',
						'zMemory-Graph Memory Identifier-667',
						'zMemory-Notification State-668',
						'zMemory-Cloud Local State-669',
						'zMemory-Cloud Delete State-670',
						'zMemory-Story Color Grade Kind-671',
						'zMemory-Story Serialized Title Category-672',
						'zMemory-Syndicated Content State-673',
						'zMemory-Search Index Rebuild State-674',
						'zMemory-Black Listed Feature-675',
						'zMoment-UUID-4TableStart-676',
						'zMoment-Aggregation Score-677',
						('zMoment-Start Date-678', 'datetime'),
						('zMoment-Representative Date-679', 'datetime'),
						'zMoment-Timezone Offset-680',
						('zMoment-Modification Date-681', 'datetime'),
						('zMoment-End Date-682', 'datetime'),
						'zMoment-SubTitle-683',
						'zMoment-Title-684',
						'zMoment-Originator State-685',
						'zMoment-Sharing Composition-686',
						'zMoment-Cached Count Shared-687',
						'zMoment-Processed Location-688',
						'zMoment-Approx Latitude-689',
						'zMoment-Approx Longitude-690',
						'zMoment-GPS Horizontal Accuracy-691',
						'zMoment-Cache Count-692',
						'zMoment-Cached Photos Count-693',
						'zMoment-Cached Videos Count-694',
						'zMoment-Trashed State-695',
						'SBKAzSugg-UUID-4TableStart-696',
						'SBKAzSugg-Suggestion Context-697',
						'SBKAzSugg-Sharing Composition-698',
						('SBKAzSugg-Start Date-699', 'datetime'),
						'SBKAzSugg-State-700',
						'SBKAzSugg-Featured State-701',
						'SBKAzSugg-Notification State-702',
						('SBKAzSugg-Creation Date-703', 'datetime'),
						('SBKAzSugg-End Date-704', 'datetime'),
						('SBKAzSugg-Activation Date-705', 'datetime'),
						('SBKAzSugg-Expunge Date-706', 'datetime'),
						('SBKAzSugg-Relevant Until Date-707', 'datetime'),
						'SBKAzSugg-Title-708',
						'SBKAzSugg-Sub Title-709',
						'SBKAzSugg-Cached Count-710',
						'SBKAzSugg-Cahed Photos Count-711',
						'SBKAzSugg-Cached Videos Count-712',
						'SBKAzSugg-Type-713',
						'SBKAzSugg-Sub Type-714',
						'SBKAzSugg-Action Data-715',
						'SBKAzSugg-Version-716',
						'SBKAzSugg-Cloud Local State-717',
						'SBKAzSugg-Cloud Delete State-718',
						'SBRAzSugg-UUID-4TableStart-719',
						'SBRAzSugg-Suggestion Context-720',
						'SBRAzSugg-Sharing Composition-721',
						('SBRAzSugg-Start Date-722', 'datetime'),
						'SBRAzSugg-State-723',
						'SBRAzSugg-Featured State-724',
						'SBRAzSugg-Notification State-725',
						('SBRAzSugg-Creation Date-726', 'datetime'),
						('SBRAzSugg-End Date-727', 'datetime'),
						('SBRAzSugg-Activation Date-728', 'datetime'),
						('SBRAzSugg-Expunge Date-729', 'datetime'),
						('SBRAzSugg-Relevant Until Date-730', 'datetime'),
						'SBRAzSugg-Title-731',
						'SBRAzSugg-Sub Title-732',
						'SBRAzSugg-Cached Count-733',
						'SBRAzSugg-Cahed Photos Count-734',
						'SBRAzSugg-Cached Videos Count-735',
						'SBRAzSugg-Type-736',
						'SBRAzSugg-Sub Type-737',
						'SBRAzSugg-Action Data-738',
						'SBRAzSugg-Version-739',
						'SBRAzSugg-Cloud Local State-740',
						'SBRAzSugg-Cloud Delete State-741',
						'zMedAnlyAstAttr-Media Analysis Version-742',
						'zMedAnlyAstAttr-Audio Classification-743',
						'zMedAnlyAstAttr-Best Video Range Duration Time Scale-744',
						'zMedAnlyAstAttr-Best Video Range Start Time Scale-745',
						'zMedAnlyAstAttr-Best Video Range Duration Value-746',
						'zMedAnlyAstAttr-Best Video Range Start Value-747',
						'zMedAnlyAstAttr-Packed Best Playback Rect-748',
						'zMedAnlyAstAttr-Activity Score-749',
						'zMedAnlyAstAttr-Video Score-750',
						'zMedAnlyAstAttr-Audio Score-751',
						'zMedAnlyAstAttr-Wallpaper Score-752',
						'zMedAnlyAstAttr-AutoPlay Suggestion Score-753',
						'zMedAnlyAstAttr-Blurriness Score-754',
						'zMedAnlyAstAttr-Exposure Score-755',
						'zMedAnlyAstAttr-Probable Rotation Direction Confidence-756',
						'zMedAnlyAstAttr-Probable Rotation Direction-757',
						'zMedAnlyAstAttr-Screen Time Device Image Sensitivity-758',
						'zAssetAnalyState-Asset UUID-4TableStart-759',
						'zAssetAnalyState-Analyisis State-760',
						'zAssetAnalyState-Worker Flags-761',
						'zAssetAnalyState-Worker Type-762',
						('zAssetAnalyState-Ignore Until Date-763', 'datetime'),
						('zAssetAnalyState-Last Ignored Date-764', 'datetime'),
						('zAssetAnalyState-Sort Token-765', 'datetime'),
						'zMedAnlyAstAttr-Character Recognition Attr-766',
						'zCharRecogAttr-Algorithm Version-767',
						'zCharRecogAttr-Adjustment Version-768',
						'zMedAnlyAstAttr-Visual Search Attributes-769',
						'zVisualSearchAttr-Algorithm Version-770',
						'zVisualSearchAttr-Adjustment Version-771',
						'zAsset-Overall Aesthetic Score-772',
						'zCompAssetAttr-Behavioral Score-773',
						'zCompAssetAttr-Failure Score zCompAssetAttr-774',
						'zCompAssetAttr-Harmonious Color Score-775',
						'zCompAssetAttr-Immersiveness Score-776',
						'zCompAssetAttr-Interaction Score-777',
						'zCompAssetAttr-Intersting Subject Score-778',
						'zCompAssetAttr-Intrusive Object Presence Score-779',
						'zCompAssetAttr-Lively Color Score-780',
						'zCompAssetAttr-Low Light-781',
						'zCompAssetAttr-Noise Score-782',
						'zCompAssetAttr-Pleasant Camera Tilt Score-783',
						'zCompAssetAttr-Pleasant Composition Score-784',
						'zCompAssetAttr-Pleasant Lighting Score-785',
						'zCompAssetAttr-Pleasant Pattern Score-786',
						'zCompAssetAttr-Pleasant Perspective Score-787',
						'zCompAssetAttr-Pleasant Post Processing Score-788',
						'zCompAssetAttr-Pleasant Reflection Score-789',
						'zCompAssetAttrPleasant Symmetry Score-790',
						'zCompAssetAttr-Sharply Focused Subject Score-791',
						'zCompAssetAttr-Tastfully Blurred Score-792',
						'zCompAssetAttr-Well Chosen Subject Score-793',
						'zCompAssetAttr-Well Framed Subject Score-794',
						'zCompAssetAttr-Well Timeed Shot Score-795',
						'zCldRes-Asset UUID-4TableStart-796',
						'zCldRes-Cloud Local State-797',
						'zCldRes-File Size-798',
						'zCldRes-Height-799',
						'zCldRes-Is Available-800',
						'zCldRes-Is Locally Available-801',
						'zCldRes-Prefetch Count-802',
						'zCldRes-Source Type-803',
						'zCldRes-Type-804',
						'zCldRes-Width-805',
						('zCldRes-Date Created-806', 'datetime'),
						('zCldRes-Last OnDemand Download Date-807', 'datetime'),
						('zCldRes-Last Prefetch Date-808', 'datetime'),
						'zCldRes-Prunedat-809',
						'zCldRes-File Path-810',
						'zCldRes-Fingerprint-811',
						'zCldRes-Item ID-812',
						'zCldRes-UniID-813',
						'zUserFeedback-UUID-4TableStart-814',
						'zUserFeedback-Feature-815',
						'zUserFeedback-Type-816',
						('zUserFeedback-Last Modified Date-817', 'datetime'),
						'zUserFeedback-Context-818',
						'zUserFeedback-Cloud Local State-819',
						'zUserFeedback-Cloud Delete State-820',
						'zAddAssetAttr-zPK-821',
						'zAddAssetAttr-zENT-822',
						'ZAddAssetAttr-zOPT-823',
						'zAddAssetAttr-zAsset= zAsset_zPK-824',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-825',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-826',
						'zAddAssetAttr-Master Fingerprint-827',
						'zAddAssetAttr-Public Global UUID-828',
						'zAddAssetAttr-Deferred Photo Identifier-829',
						'zAddAssetAttr-Original Assets UUID-830',
						'zAddAssetAttr-Import Session ID-831',
						'zAddAssetAttr-Originating Asset Identifier-832',
						'zAddAssetAttr.Adjusted Fingerprint-833',
						'zAlbumList-zPK= Album List Key-834',
						'zAlbumList-zENT-835',
						'zAlbumList-zOPT-836',
						'zAlbumList-ID Key-837',
						'zAlbumList-UUID-838',
						'zAsset-zPK-839',
						'zAsset-zENT-840',
						'zAsset-zOPT-841',
						'zAsset-Master= zCldMast-zPK-842',
						'zAsset-Extended Attributes= zExtAttr-zPK-843',
						'zAsset-Import Session Key-844',
						'zAsset-Trashed by Participant= zSharePartic_zPK-845',
						'zAsset-Photo Analysis Attributes Key-846',
						'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-847',
						'zAsset-FOK-Cloud Feed Asset Entry Key-848',
						'zAsset-Moment Share Key= zShare-zPK-849',
						'zAsset-zMoment Key= zMoment-zPK-850',
						'zAsset-Computed Attributes Asset Key-851',
						'zAsset-Highlight Being Assets-HBA Key-852',
						'zAsset-Highlight Being Extended Assets-HBEA Key-853',
						'zAsset-Highlight Being Key Asset Private-HBKAP Key-854',
						'zAsset-Highlight Being Key Asset Shared-HBKAS Key-855',
						'zAsset-Highligh Being Summary Assets-HBSA Key-856',
						'zAsset-Day Group Highlight Being Assets-DGHBA Key-857',
						'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key-858',
						'zAsset-Day Group Highlight Being Key Asset Private-DGHBKAP Key-859',
						'zAsset-Day Group Highlight Being Key Asset Shared-DGHBKAS Key-860',
						'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key-861',
						'zAsset-Month Highlight Being Key Asset Private-MHBKAP Key-862',
						'zAsset-Month Highlight Being Key Asset Shared-MHBKAS Key-863',
						'zAsset-Year Highlight Being Key Asset Private-YHBKAP Key-864',
						'zAsset-Year Highlight Being Key Asset Shared-YHBKAS Key-865',
						'zAsset-Promotion Score-866',
						'zAsset-Media Analysis Attributes Key-867',
						'zAsset-Media Group UUID-868',
						'zAsset-UUID = store.cloudphotodb-869',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-870',
						'zAsset.Cloud Collection GUID-871',
						'zAsset-Avalanche UUID-872',
						'zAssetAnalyState-zPK-873',
						'zAssetAnalyState-zEnt-874',
						'zAssetAnalyState-zOpt-875',
						'zAssetAnalyState-Asset= zAsset-zPK-876',
						'zAssetAnalyState-Asset UUID-877',
						'zAsstContrib-zPK-878',
						'zAsstContrib-zEnt-879',
						'zAsstContrib-zOpt-880',
						'zAsstContrib-3Library Scope Asset Contributors= zAssset-zPK-881',
						'zAsstContrib-Participant= zSharePartic-zPK-882',
						'zAssetDes-zPK-883',
						'zAssetDes-zENT-884',
						'zAssetDes-zOPT-885',
						'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK-886',
						'zCharRecogAttr-zPK-887',
						'zCharRecogAttr-zENT-888',
						'zCharRecogAttr-zOPT-889',
						'zCharRecogAttr-MedAssetAttr= zMedAnlyAstAttr-zPK-890',
						'zCldFeedEnt-zPK= zCldShared keys-891',
						'zCldFeedEnt-zENT-892',
						'zCldFeedEnt-zOPT-893',
						'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-894',
						'zCldFeedEnt-Entry Invitation Record GUID-895',
						'zCldFeedEnt-Entry Cloud Asset GUID-896',
						'zCldMast-zPK= zAsset-Master-897',
						'zCldMast-zENT-898',
						'zCldMast-zOPT-899',
						'zCldMast-Moment Share Key= zShare-zPK-900',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-901',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-902',
						'zCldMast-Originating Asset ID-903',
						'zCldMast-Import Session ID- AirDrop-StillTesting-904',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-905',
						'CMzCldMastMedData-zENT-906',
						'CMzCldMastMedData-zOPT-907',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-908',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-909',
						'AAAzCldMastMedData-zENT-910',
						'AAAzCldMastMedData-zOPT-911',
						'AAAzCldMastMedData-CldMast key-912',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-913',
						'zCldRes-zPK-914',
						'zCldRes-zENT-915',
						'zCldRes-zOPT-916',
						'zCldRes-Asset= zAsset-zPK-917',
						'zCldRes-Cloud Master= zCldMast-zPK-918',
						'zCldRes-Asset UUID-919',
						'zCldShareAlbumInvRec-zPK-920',
						'zCldShareAlbumInvRec-zEnt-921',
						'zCldShareAlbumInvRec-zOpt-922',
						'zCldShareAlbumInvRec-Album Key-923',
						'zCldShareAlbumInvRec-FOK Album Key-924',
						'zCldShareAlbumInvRec-Album GUID-925',
						'zCldShareAlbumInvRec-zUUID-926',
						'zCldShareAlbumInvRec-Cloud GUID-927',
						'zCldSharedComment-zPK-928',
						'zCldSharedComment-zENT-929',
						'zCldSharedComment-zOPT-930',
						'zCldSharedComment-Commented Asset Key= zAsset-zPK-931',
						'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-932',
						'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-933',
						'zCldSharedComment-Liked Asset Key= zAsset-zPK-934',
						'zCldSharedComment-CldFeedLikeCommentEntry Key-935',
						'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-936',
						'zCldSharedComment-Cloud GUID-937',
						'zCompAssetAttr-zPK-938',
						'zCompAssetAttr-zEnt-939',
						'zCompAssetAttr-zOpt-940',
						'zCompAssetAttr-Asset Key-941',
						'zDetFace-zPK-942',
						'zDetFace-zEnt-943',
						'zDetFace.zOpt-944',
						'zDetFace-Asset= zAsset-zPK or Asset Containing Face-945',
						'zDetFace-Person= zPerson-zPK-946',
						'zDetFace-Person Being Key Face-947',
						'zDetFace-Face Print-948',
						'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-949',
						'zDetFace-FaceGroup= zDetFaceGroup-zPK-950',
						'zDetFace-UUID-951',
						'zDetFaceGroup-zPK-952',
						'zDetFaceGroup-zENT-953',
						'zDetFaceGroup-zOPT-954',
						'zDetFaceGroup-AssocPerson= zPerson-zPK-955',
						'zDetFaceGroup-KeyFace= zDetFace-zPK-956',
						'zDetFaceGroup-UUID-957',
						'zDetFacePrint-zPK-958',
						'zDetFacePrint-zEnt-959',
						'zDetFacePrint-zOpt-960',
						'zDetFacePrint-Face Key-961',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-962',
						'zExtAttr-zENT-963',
						'zExtAttr-zOPT-964',
						'zExtAttr-Asset Key-965',
						'zFaceCrop-zPK-966',
						'zFaceCrop-zEnt-967',
						'zFaceCrop-zOpt-968',
						'zFaceCrop-Asset Key-969',
						'zFaceCrop-Invalid Merge Canidate Person UUID-970',
						'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-971',
						'zFaceCrop-Face Key-972',
						'zFaceCrop-UUID-973',
						'zGenAlbum-zPK=26AlbumLists= 26Albums-974',
						'zGenAlbum-zENT-975',
						'zGenAlbum-zOpt-976',
						'zGenAlbum-Key Asset-Key zAsset-zPK-977',
						'zGenAlbum-Secondary Key Asset-978',
						'zGenAlbum-Tertiary Key Asset-979',
						'zGenAlbum-Custom Key Asset-980',
						'zGenAlbum-Parent Folder Key= zGenAlbum-zPK-981',
						'zGenAlbum-FOK Parent Folder-982',
						'zGenAlbum-zSyndicate-983',
						'zGenAlbum-UUID-984',
						'SWYConverszGenAlbum-UUID-985',
						'zGenAlbum-Cloud_GUID = store.cloudphotodb-986',
						'SWYConverszGenAlbum-Cloud GUID-987',
						'zGenAlbum-Project Render UUID-988',
						'SWYConverszGenAlbum-Project Render UUID-989',
						'zIntResou-zPK-990',
						'zIntResou-zENT-991',
						'zIntResou-zOPT-992',
						'zIntResou-Asset= zAsset_zPK-993',
						'zIntResou-Fingerprint-994',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-995',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-996',
						'zMedAnlyAstAttr-zEnt-997',
						'zMedAnlyAstAttr-zOpt-998',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-999',
						'zMemory-zPK-1000',
						'zMemory-zENT-1001',
						'zMemory-zOPT-1002',
						'zMemory-Key Asset= zAsset-zPK-1003',
						'zMemory-UUID-1004',
						'zMoment-zPK-1005',
						'zMoment-zENT-1006',
						'zMoment-zOPT-1007',
						'zMoment-Highlight Key-1008',
						'zMoment-UUID-1009',
						'zPerson-zPK=zDetFace-Person-1010',
						'zPerson-zEnt-1011',
						'zPerson-zOpt-1012',
						'zPerson-Share Participant= zSharePartic-zPK-1013',
						'zPerson-KeyFace=zDetFace-zPK-1014',
						'zPerson-Assoc Face Group Key-1015',
						'zPerson-Person UUID-1016',
						'zPhotoAnalysisAssetAttr-zPK-1017',
						'zPhotoAnalysisAssetAttr-zEnt-1018',
						'zPhotoAnalysisAssetAttr-zOpt-1019',
						'zPhotoAnalysisAssetAttr-zAsset = zAsset-zPK-1020',
						'zSceneP-zPK-1021',
						'zSceneP-zENT-1022',
						'zSceneP-zOPT-1023',
						'zShare-zPK-1024',
						'zShare-zENT-1025',
						'zShare-zOPT-1026',
						'zShare-UUID-1027',
						'SPLzShare-UUID-1028',
						'zShare-Scope ID = store.cloudphotodb-1029',
						'zSharePartic-zPK-1030',
						'zSharePartic-zENT-1031',
						'zSharePartic-zOPT-1032',
						'zSharePartic-Share Key= zShare-zPK-1033',
						'zSharePartic-Person= zPerson-zPK-1034',
						'zSharePartic-UUID-1035',
						'SBKAzSugg-zPK-1036',
						'SBKAzSugg-zENT-1037',
						'SBKAzSugg-zOPT-1038',
						'SBKAzSugg-UUID-1039',
						'SBRAzSugg-zPK-1040',
						'SBRAzSugg-zENT-1041',
						'SBRAzSugg-zOPT-1042',
						'SBRAzSugg-UUID-1043',
						'z3SuggBRA-3RepAssets1-1044',
						'z3SuggBRA-58SuggBeingRepAssets-1045',
						'z3SuggBKA-58SuggBeingKeyAssets= zSugg-zPK-1046',
						'z3SuggBKA-3KeyAssets= zAsset-zPK-1047',
						'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key-1048',
						'zUnmAdj-zOPT-1049',
						'zUnmAdj-zENT-1050',
						'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK-1051',
						'zUnmAdj-UUID-1052',
						'zUnmAdj-Other Adjustments Fingerprint-1053',
						'zUnmAdj-Similar to Orig Adjustments Fingerprint-1054',
						'zUserFeedback-zPK-1055',
						'zUserFeedback-zENT-1056',
						'zUserFeedback-zOPT-1057',
						'zUserFeedback-Person= zPerson-zPK-1058',
						'zUserFeedback-Memory= zMemory-zPK-1059',
						'zUserFeedback-UUID-1060',
						'zVisualSearchAttr-zPK-1061',
						'zVisualSearchAttr-zENT-1062',
						'zVisualSearchAttr-zOPT-1063',
						'zVisualSearchAttr-MedAssetAttr= zMedAnlyAstAttr-zPK-1064',
						'z27AlbumList-27Albums= zGenAlbum-zPK-1065',
						'z27AlbumList-Album List Key-1066',
						'z27AlbumList-FOK27Albums Key-1067',
						'z28Assets-28Albums= zGenAlbum-zPK-1068',
						'z28Assets-3Asset Key= zAsset-zPK in the Album-1069',
						'z28Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY-1070',
						'z3MemoryBMCAs-3MovieCuratedAssets= zAsset-zPK-1071',
						'z3MemoryBCAs-3CuratedAssets= zAsset-zPK-1072',
						'z3MemoryBCAs-44MemoriesBeingCuratedAssets= zMemory-zPK-1073',
						'z3MemoryBECAs-3ExtCuratedAssets= zAsset-zPK-1074',
						'z3MemoryBECAs-44MemoriesBeingExtCuratedAssets= zMemory-zPK-1075',
						'z3MemoryBRAs-3RepresentativeAssets= zAsset-zPK-1076',
						'z3MemoryBRAs-44RepresentativeAssets= zMemory-zPK-1077',
						'z3MemoryBUCAs-3UserCuratedAssets= zAsset-zPK-1078',
						'z3MemoryBUCAs-44MemoriesBeingUserCuratedAssets= zMemory-zPK-1079',
						'z3MemoryBCAs-44Memories Being Custom User Assets-1080',
						'z3MemoryBCAs-3Custom User Assets-1081',
						'z3MemoryBCAs-FOK-3Custom User Assets-1082')
		data_list = get_sqlite_db_records(source_path, query)

		return data_headers, data_list, source_path

@artifact_processor
def Ph96_2iOS16RefforAssetAnalysisSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
	for source_path in files_found:
		source_path = str(source_path)

		if source_path.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if (version.parse(iosversion) <= version.parse("15.8.2")) or (version.parse(iosversion) >= version.parse("17")):
		logfunc("Unsupported version for Syndication.photoslibrary for iOS " + iosversion)
		return (), [], source_path
	if (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
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
		CASE zAsset.ZBUNDLESCOPE
			WHEN 0 THEN '0-WheniCldPhtos-ON-AssetNotInSharedAlbum_or_WheniCldPhtos-OFF-AssetOnLocalDevice-0'
			WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
			WHEN 2 THEN '2-WheniCldPhtos-ON-AssetInCloudSharedAlbum-2'
			WHEN 3 THEN '3-WheniCldPhtos-ON-AssetIsInSWYConversation-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
		END AS 'zAsset-Bundle Scope',
		CASE zAsset.ZSYNDICATIONSTATE
			WHEN 0 THEN '0-LPLPs-NA_or_SYWPs-Received-SWY_Synd_Asset-0'
			WHEN 1 THEN '1-SWYPs-Sent-SWY_Synd_Asset-1'
			WHEN 2 THEN '2-SWYPs-Manually-Saved_SWY_Synd_Asset-2'
			WHEN 3 THEN '3-SWYPs-STILLTESTING_Sent-SWY-3'
			WHEN 8 THEN '8-SWYPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
			WHEN 9 THEN '9-SWYPs-STILLTESTING_Sent_SWY-9'
			WHEN 10 THEN '10-SWYPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
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
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
		CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
			WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
			WHEN 1 THEN '1-Asset-In-Active-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
		END AS 'zAsset-Active Library Scope Participation State -4QueryStart',
		CASE zAsset.ZLIBRARYSCOPESHARESTATE
			WHEN 0 THEN '0-Asset-Not-In-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
		END AS 'zAsset-Library Scope Share State- StillTesting -4QueryStart',
		zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count-SPL -4QueryStart',
		zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count-SPL -4QueryStart',
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
		SWYConverszGenAlbum.ZUUID AS 'SWYConverszGenAlbum-UUID-4QueryStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4QueryStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4QueryStart',
		SWYConverszGenAlbum.ZCLOUDGUID AS 'SWYConverszGenAlbum-Cloud GUID-4QueryStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4QueryStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4QueryStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4QueryStart',
		SWYConverszGenAlbum.ZPROJECTRENDERUUID AS 'SWYConverszGenAlbum-Project Render UUID-4QueryStart',
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
		CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud_Local_State-4QueryStart',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Creation Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Cloud Creation Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- Cloud Creation Date- 4QueryStart',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- Start Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- Start Date- 4QueryStart',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum- End Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum- End Date- 4QueryStart',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date- 4QueryStart',
		DateTime(SWYConverszGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Subscription Date- 4QueryStart',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title- 4QueryStart',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied- 4QueryStart',
		SWYConverszGenAlbum.ZTITLE AS 'SWYConverszGenAlbum- Title -User&System Applied- 4QueryStart',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY- 4QueryStart',
		zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK -4QueryStart',
		SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY- 4QueryStart',
		zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier- 4QueryStart',
		SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier- 4QueryStart',
		CASE SWYConverszGenAlbum.ZSYNDICATE
			WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
		END AS 'SWYConverszGenAlbum- Syndicate-4QueryStart',
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
		CASE SWYConverszGenAlbum.ZKIND
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
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
		END AS 'SWYConverszGenAlbum-Album Kind- 4QueryStart',		
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
		zAsset.ZVIDEODEFERREDPROCESSINGNEEDED AS 'zAsset-Video Deferred Processing Needed',
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
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK-4QueryStart',
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
		zAsset.ZISMAGICCARPET AS 'zAsset-Is Magic Carpet-QuicktimeMOVfile',
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
		zPhotoAnalysisAssetAttr.ZWALLPAPERPROPERTIESVERSION AS 'zPhotoAnalysisAssetAttr-Wallpaper Properties Version',
		DateTime(zPhotoAnalysisAssetAttr.ZWALLPAPERPROPERTIESTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zPhotoAnalysisAssetAttr-Wallpaper Properties Timestamp',
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
		CASE zAsset.ZLIBRARYSCOPESHARESTATE
			WHEN 0 THEN '0-Asset-Not-In-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZLIBRARYSCOPESHARESTATE || ''
		END AS 'zAsset-Library Scope Share State- StillTesting',
		CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
			WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
			WHEN 1 THEN '1-Asset-In-Active-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
		END AS 'zAsset-Active Library Scope Participation State',
		zAddAssetAttr.ZLIBRARYSCOPEASSETCONTRIBUTORSTOUPDATE AS 'zAddAssetAttr-Library Scope Asset Contributors To Update',
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
		CASE zSharePartic.Z54_SHARE
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.Z54_SHARE || ''
		END AS 'zSharePartic-z54SHARE',
		CASE SPLzSharePartic.Z54_SHARE
			WHEN 55 THEN '55-SPL-Entity-55'
			WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
			WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
			WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.Z54_SHARE || ''
		END AS 'SPLzSharePartic-z54SHARE',
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
		zShare.ZCLOUDITEMCOUNT AS 'zShare-Cloud Item Count-CMM',
		SPLzShare.ZCLOUDITEMCOUNT AS 'SPLzShare-Cloud Item Count-SPL',
		zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
		SPLzShare.ZASSETCOUNT AS 'SPLzShare-Asset Count-SPL',
		zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count-CMM',
		SPLzShare.ZCLOUDPHOTOCOUNT AS 'SPLzShare-Cloud Photo Count-SPL',
		zShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-CMM',
		SPLzShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'SPLzShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-SPL',
		zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
		SPLzShare.ZPHOTOSCOUNT AS 'SPLzShare-Photos Count-CMM-SPL',
		zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
		SPLzShare.ZUPLOADEDPHOTOSCOUNT AS 'SPLzShare-Uploaded Photos Count-SPL',
		zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count-CMM',
		SPLzShare.ZCLOUDVIDEOCOUNT AS 'SPLzShare-Cloud Video Count-SPL',
		zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
		SPLzShare.ZVIDEOSCOUNT AS 'SPLzShare-Videos Count-SPL',
		zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
		SPLzShare.ZUPLOADEDVIDEOSCOUNT AS 'SPLzShare-Uploaded Videos Count-SPL',
		zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',
		SPLzShare.ZFORCESYNCATTEMPTED AS 'SPLzShare-Force Sync Attempted-SPL',
		CASE zShare.ZCLOUDLOCALSTATE
			WHEN 1 THEN '1-LocalandCloud-SPL-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDLOCALSTATE || ''
		END AS 'zShare-Cloud Local State-CMM',
		CASE SPLzShare.ZCLOUDLOCALSTATE
			WHEN 1 THEN '1-LocalandCloud-SPL-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZCLOUDLOCALSTATE || ''
		END AS 'SPLzShare-Cloud Local State-SPL',
		CASE zShare.ZSCOPESYNCINGSTATE
			WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPESYNCINGSTATE || ''
		END AS 'zShare-Scope Syncing State-CMM',
		CASE SPLzShare.ZSCOPESYNCINGSTATE
			WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSCOPESYNCINGSTATE || ''
		END AS 'SPLzShare-Scope Syncing State-SPL',
		CASE zShare.ZAUTOSHAREPOLICY
			WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZAUTOSHAREPOLICY || ''
		END AS 'zShare-Auto Share Policy-CMM',
		CASE SPLzShare.ZAUTOSHAREPOLICY
			WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZAUTOSHAREPOLICY || ''
		END AS 'SPLzShare-Auto Share Policy-SPL',
		CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-CMM-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'zShare-Should Notify On Upload Completion-CMM',
		CASE SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
			WHEN 0 THEN '0-DoNotNotify-SPL-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
		END AS 'SPLzShare-Should Notify On Upload Completion-SPL',
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK-SPL-CMM',
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
		DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date-CMM',
		DateTime(SPLzShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Trashed Date-SPL',
		DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-LastParticipant Asset Trash Notification Date-CMM',
		DateTime(SPLzShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-LastParticipant Asset Trash Notification Date-SPL',
		DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Last Participant Asset Trash Notification View Date-CMM',
		DateTime(SPLzShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Last Participant Asset Trash Notification View Date-SPL',
		CASE zShare.ZEXITSOURCE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSOURCE || ''
		END AS 'zShare-Exit Source-CMM',
		CASE SPLzShare.ZEXITSOURCE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZEXITSOURCE || ''
		END AS 'SPLzShare-Exit Source-SPL',
		CASE zShare.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSTATE || ''
		END AS 'zShare-SPL_Exit State-CMM',
		CASE SPLzShare.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZEXITSTATE || ''
		END AS 'SPLzShare-SPL_Exit State-SPL',
		CASE zShare.ZEXITTYPE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zShare.ZEXITTYPE || ''
		END AS 'zShare-Exit Type-CMM',
		CASE SPLzShare.ZEXITTYPE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZEXITTYPE || ''
		END AS 'SPLzShare-Exit Type-SPL',
		CASE zShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'zShare-Should Ignor Budgets-CMM',
		CASE SPLzShare.ZSHOULDIGNOREBUDGETS
			WHEN 1 THEN '1-StillTesting-CMM-1'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSHOULDIGNOREBUDGETS || ''
		END AS 'SPLzShare-Should Ignor Budgets-SPL',
		CASE zShare.ZPREVIEWSTATE
			WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
			ELSE 'Unknown-New-Value!: ' || zShare.ZPREVIEWSTATE || ''
		END AS 'zShare-Preview State-CMM',
		CASE SPLzShare.ZPREVIEWSTATE
			WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZPREVIEWSTATE || ''
		END AS 'SPLzShare-Preview State-SPL',
		zShare.ZPREVIEWDATA AS 'zShare-Preview Data-CMM',
		SPLzShare.ZPREVIEWDATA AS 'SPLzShare-Preview Data-SPL',
		zShare.ZRULESDATA AS 'zShare-Rules-CMM',
		SPLzShare.ZRULESDATA AS 'SPLzShare-Rules-SPL',
		zShare.ZTHUMBNAILIMAGEDATA AS 'zShare-Thumbnail Image Data-CMM',
		SPLzShare.ZTHUMBNAILIMAGEDATA AS 'SPLzShare-Thumbnail Image Data-SPL',
		CASE zShare.ZPARTICIPANTCLOUDUPDATESTATE
			WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
			ELSE 'Unknown-New-Value!: ' || zShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
		END AS 'zShare-Participant Cloud Update State-CMM',
		CASE SPLzShare.ZPARTICIPANTCLOUDUPDATESTATE
			WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
			ELSE 'Unknown-New-Value!: ' || SPLzShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
		END AS 'SPLzShare-Participant Cloud Update State-SPL',
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
			WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
			WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
		END AS 'zSharePartic-Is Current User',
		CASE SPLzSharePartic.ZISCURRENTUSER
			WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
			WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
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
		zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
		SPLzSharePartic.ZPARTICIPANTID AS 'SPLzSharePartic-Participant ID',
		zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
		SPLzSharePartic.ZUSERIDENTIFIER AS 'SPLzSharePartic-User ID',
		zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK-4TableStart',
		SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK-4TableStart',
		zSharePartic.Z_PK AS 'zSharePartic-zPK-4TableStart',
		zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
		SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
		zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
		SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
		CASE zSharePartic.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || zSharePartic.ZEXITSTATE || ''
		END AS 'zSharePartic-Exit State',
		CASE SPLzSharePartic.ZEXITSTATE
			WHEN 0 THEN '0-NA_SPL_StillTesting'
			ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZEXITSTATE || ''
		END AS 'SPLzSharePartic-Exit State',
		ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID-4TableStart',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
		SWYConverszGenAlbum.ZUUID AS 'SWYConverszGenAlbum-UUID-4TableStart',
		ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID-4TableStart',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart',
		SWYConverszGenAlbum.ZCLOUDGUID AS 'SWYConverszGenAlbum-Cloud GUID-4TableStart',
		zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID-4TableStart',
		zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID-4TableStart',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID-4TableStart',
		SWYConverszGenAlbum.ZPROJECTRENDERUUID AS 'SWYConverszGenAlbum-Project Render UUID-4TableStart',
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
		CASE SWYConverszGenAlbum.ZKIND
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
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
		END AS 'SWYConverszGenAlbum-Album Kind',
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
		CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
			WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos-OFF=Generic_Album-0'
			WHEN 1 THEN '1-iCldPhotos-ON=Asset_In_Generic_Album-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud_Local_State',
		ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
		zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
		SWYConverszGenAlbum.ZTITLE AS 'SWYConverszGenAlbum- Title -User&System Applied',
		zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum-Import Session ID-SWY',
		zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
		SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
		zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',
		SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
		CASE SWYConverszGenAlbum.ZSYNDICATE
			WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
		END AS 'SWYConverszGenAlbum- Syndicate',
		DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
		DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
		DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Creation Date',
		DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
		DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
		DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
		DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
		DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Subscription Date',
		ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
		zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',
		SWYConverszGenAlbum.ZPENDINGITEMSCOUNT AS 'SWYConverszGenAlbum-Pending Items Count',
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
		CASE SWYConverszGenAlbum.ZPENDINGITEMSTYPE
			WHEN 1 THEN 'No-1'
			WHEN 24 THEN '24-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPENDINGITEMSTYPE || ''
		END AS 'SWYConverszGenAlbum-Pending Items Type',
		zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
		SWYConverszGenAlbum.ZCACHEDPHOTOSCOUNT AS 'SWYConverszGenAlbum- Cached Photos Count',
		zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',
		SWYConverszGenAlbum.ZCACHEDVIDEOSCOUNT AS 'SWYConverszGenAlbum- Cached Videos Count',
		zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
		SWYConverszGenAlbum.ZCACHEDCOUNT AS 'SWYConverszGenAlbum- Cached Count',
		ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
		zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',
		SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
		CASE zGenAlbum.ZHASUNSEENCONTENT
			WHEN 0 THEN 'No Unseen Content-StillTesting-0'
			WHEN 1 THEN 'Unseen Content-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
		END AS 'zGenAlbum-Has Unseen Content',
		CASE SWYConverszGenAlbum.ZHASUNSEENCONTENT
			WHEN 0 THEN 'No Unseen Content-StillTesting-0'
			WHEN 1 THEN 'Unseen Content-StillTesting-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZHASUNSEENCONTENT || ''
		END AS 'SWYConverszGenAlbum-Has Unseen Content',
		zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',
		SWYConverszGenAlbum.ZUNSEENASSETSCOUNT AS 'SWYConverszGenAlbum-Unseen Asset Count',
		CASE zGenAlbum.ZISOWNED
			WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
			WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
		END AS 'zGenAlbum-is Owned',
		CASE SWYConverszGenAlbum.ZISOWNED
			WHEN 0 THEN 'SWYConverszGenAlbum-Not Owned by Device Apple Acnt-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Owned by Device Apple Acnt-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISOWNED || ''
		END AS 'SWYConverszGenAlbum-is Owned',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
			WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
			WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
		END AS 'zGenAlbum-Cloud Relationship State',
		CASE SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATE
			WHEN 0 THEN 'SWYConverszGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
			WHEN 2 THEN 'SWYConverszGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud Relationship State',
		CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
			WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
		END AS 'zGenAlbum-Cloud Relationship State Local',
		CASE SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
			WHEN 0 THEN 'SWYConverszGenAlbum-Shared Album Accessible Local Device-0'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
		END AS 'SWYConverszGenAlbum-Cloud Relationship State Local',
		zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',
		SWYConverszGenAlbum.ZCLOUDOWNEREMAILKEY AS 'SWYConverszGenAlbum-Cloud Owner Mail Key',
		zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',
		SWYConverszGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'SWYConverszGenAlbum-Cloud Owner Frist Name',
		zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',
		SWYConverszGenAlbum.ZCLOUDOWNERLASTNAME AS 'SWYConverszGenAlbum-Cloud Owner Last Name',
		zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
		SWYConverszGenAlbum.ZCLOUDOWNERFULLNAME AS 'SWYConverszGenAlbum-Cloud Owner Full Name',
		zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',
		SWYConverszGenAlbum.ZCLOUDPERSONID AS 'SWYConverszGenAlbum-Cloud Person ID',
		zAsset.ZCLOUDOWNERHASHEDPERSONID AS 'zAsset-Cloud Owner Hashed Person ID',
		zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',
		SWYConverszGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'SWYConverszGenAlbum-Cloud Owner Hashed Person ID',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
		END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
			WHEN 0 THEN 'SWYConverszGenAlbum-Local Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Local Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
		END AS 'SWYConverszGenAlbum-Local Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
		END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
			WHEN 0 THEN 'SWYConverszGenAlbum-Cloud Single Contributor Enabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Cloud Multi-Contributors Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
		END AS 'SWYConverszGenAlbum-Cloud Multi-Contributors Enabled',
		CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
			WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
		END AS 'zGenAlbum-Cloud Album Sub Type',
		CASE SWYConverszGenAlbum.ZCLOUDALBUMSUBTYPE
			WHEN 0 THEN 'SWYConverszGenAlbum Multi-Contributor-0'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDALBUMSUBTYPE || ''
		END AS 'SWYConverszGenAlbum-Cloud Album Sub Type',
		DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Contribution Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Contribution Date',
		DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Last Interesting Change Date',
		DateTime(SWYConverszGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Cloud Last Interesting Change Date',
		CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
			WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
			WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
		END AS 'zGenAlbum-Cloud Notification Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDNOTIFICATIONSENABLED
			WHEN 0 THEN 'SWYConverszGenAlbum-Cloud Notifications Disabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Cloud Notifications Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
		END AS 'SWYConverszGenAlbum-Cloud Notification Enabled',
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
		CASE SWYConverszGenAlbum.ZISPINNED
			WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
		END AS 'SWYConverszGenAlbum-Pinned',
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
		CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
			WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
			WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
			WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
		END AS 'SWYConverszGenAlbum-Custom Sort Key',
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
		CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
			WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
			WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
		END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
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
		CASE SWYConverszGenAlbum.ZISPROTOTYPE
			WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
			WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
		END AS 'SWYConverszGenAlbum-Is Prototype',
		CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'ParentzGenAlbum-Project Document Type',
		CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'zGenAlbum-Project Document Type',
		CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
		END AS 'SWYConverszGenAlbum-Project Document Type',
		CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'ParentzGenAlbum-Custom Query Type',
		CASE zGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'zGenAlbum-Custom Query Type',
		CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
			WHEN 0 THEN '0-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
		END AS 'SWYConverszGenAlbum-Custom Query Type',
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
		CASE SWYConverszGenAlbum.ZTRASHEDSTATE
			WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
		END AS 'SWYConverszGenAlbum-Trashed State',
		DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
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
		CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
		END AS 'SWYConverszGenAlbum-Cloud Delete State',
		CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
			WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
			WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
		END AS 'zGenAlbum-Cloud Owner Whitelisted',
		CASE SWYConverszGenAlbum.ZCLOUDOWNERISWHITELISTED
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Owner Not Whitelisted-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Owner Whitelisted-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
		END AS 'SWYConverszGenAlbum-Cloud Owner Whitelisted',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
			WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
		END AS 'zGenAlbum-Cloud Local Public URL Enabled',
		CASE SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Local Public URL Disabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Local has Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
		END AS 'SWYConverszGenAlbum-Cloud Local Public URL Enabled',
		CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
			WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
			WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
		END AS 'zGenAlbum-Cloud Public URL Enabled',
		zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',
		CASE SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLED
			WHEN 0 THEN 'SWYConverszGenAlbum Cloud Public URL Disabled-0'
			WHEN 1 THEN 'SWYConverszGenAlbum Cloud Public URL Enabled-1'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDPUBLICURLENABLED || ''
		END AS 'SWYConverszGenAlbum-Cloud Public URL Enabled',
		SWYConverszGenAlbum.ZPUBLICURL AS 'SWYConverszGenAlbum-Public URL',
		zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',
		SWYConverszGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'SWYConverszGenAlbum-Key Asset Face Thumb Index',
		zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',
		SWYConverszGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'SWYConverszGenAlbum-Project Text Extension ID',
		zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',
		SWYConverszGenAlbum.ZUSERQUERYDATA AS 'SWYConverszGenAlbum-User Query Data',
		zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
		SWYConverszGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'SWYConverszGenAlbum-Custom Query Parameters',
		zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
		SWYConverszGenAlbum.ZPROJECTDATA AS 'SWYConverszGenAlbum-Project Data',
		CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'zGenAlbum-Search Index Rebuild State',
		CASE SWYConverszGenAlbum.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'SWYConverszGenAlbum-Search Index Rebuild State',
		CASE zGenAlbum.ZDUPLICATETYPE
			WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
			WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
			WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
		END AS 'zGenAlbum-Duplicate Type',
		CASE SWYConverszGenAlbum.ZDUPLICATETYPE
			WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
			WHEN 1 THEN '1-Duplicate Asset_Pending-Merge-1'
			WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZDUPLICATETYPE || ''
		END AS 'SWYConverszGenAlbum-Duplicate Type',
		CASE zGenAlbum.ZPRIVACYSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
			ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
		END AS 'zGenAlbum-Privacy State',
		CASE SWYConverszGenAlbum.ZPRIVACYSTATE
			WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
			WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
			WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
			ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
		END AS 'SWYConverszGenAlbum-Privacy State',
		zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID-4TableStart',
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
		zAddAssetAttr.ZFACEANALYSISVERSION AS 'zAddAssetAttr-Face Analysis Version',
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
		CASE zDetFace.ZETHNICITYTYPE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN 'Black-African American-1'
			WHEN 2 THEN 'White-2'
			WHEN 3 THEN 'Hispanic-Latino-3'
			WHEN 4 THEN 'Asian-4'
			WHEN 5 THEN 'Native Hawaiian-Other Pacific Islander-5'
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
			WHEN 1 THEN 'Black-Brown Hair Color-1'
			WHEN 2 THEN 'Brown-Blonde Hair Color-2'
			WHEN 3 THEN 'Brown-Red Hair Color-3'
			WHEN 4 THEN 'Red-White Hair Color-4'
			WHEN 5 THEN 'StillTesting-Artifical-5'
			WHEN 6 THEN 'White-Bald Hair Color-6'
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
			WHEN 1 THEN 'Disgusted-Angry-1'
			WHEN 2 THEN 'Suprised-Fearful-2'
			WHEN 3 THEN 'Neutral-3'
			WHEN 4 THEN 'Confident-Smirk-4'
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
		zAsset.ZHIGHLIGHTVISIBILITYSCORE AS 'zAsset-Highlight Visibility Score',
		zMemory.ZUUID AS 'zMemory-UUID-4TableStart',
		zMemory.ZASSETLISTPREDICATE AS 'zMemory-AssetListPredicte',
		zMemory.ZSCORE AS 'zMemory-Score',
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
		DateTime(zMemory.ZLASTENRICHMENTDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Enrichment Date',
		CASE zMemory.ZUSERACTIONOPTIONS
			WHEN 0 THEN 'User Actions Options Memory Not User Created-0'
			WHEN 1 THEN 'User Actions Options Memory User Created-1'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZUSERACTIONOPTIONS || ''
		END AS 'zMemory-User Action Options',
		CASE zMemory.ZFAVORITE
			WHEN 0 THEN 'Memory Not Favorite-0'
			WHEN 1 THEN 'Memory Favorite-1'
		END AS 'zMemory-Favorite Memory',
		zMemory.ZVIEWCOUNT AS 'zMemory-View Count',
		zMemory.ZPLAYCOUNT AS 'zMemory-Play Count',
		zMemory.ZREJECTED AS 'zMemory-Rejected',
		zMemory.ZSHARECOUNT AS 'zMemory-Share Count',
		zMemory.ZSHARINGCOMPOSITION AS 'zMemory-Sharing Composition',
		DateTime(zMemory.ZLASTMOVIEPLAYEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Movie Play Date',
		DateTime(zMemory.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zMemory-Last Viewed Date',
		zMemory.ZPENDINGPLAYCOUNT AS 'zMemory-Pending Play Count Memory',
		zMemory.ZPENDINGSHARECOUNT AS 'zMemory-Pending Share Count Memory',
		zMemory.ZPENDINGVIEWCOUNT AS 'zMemory-Pending View Count Memory',
		zMemory.ZPENDINGSTATE AS 'zMemory-Pending State',
		CASE zMemory.ZFEATUREDSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZFEATUREDSTATE || ''
		END AS 'zMemory-Featured State',
		zMemory.ZPHOTOSGRAPHVERSION AS 'zMemory-Photos Graph Version',
		zMemory.ZGRAPHMEMORYIDENTIFIER AS 'zMemory-Graph Memory Identifier',
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
		CASE zMemory.ZSTORYCOLORGRADEKIND
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSTORYCOLORGRADEKIND || ''
		END AS 'zMemory-Story Color Grade Kind',
		CASE zMemory.ZSTORYSERIALIZEDTITLECATEGORY
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSTORYSERIALIZEDTITLECATEGORY || ''
		END AS 'zMemory-Story Serialized Title Category',
		CASE zMemory.ZSYNDICATEDCONTENTSTATE
			WHEN 0 THEN '0-StillTesting'
			WHEN 1 THEN '1-StillTesting'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSYNDICATEDCONTENTSTATE || ''
		END AS 'zMemory-Syndicated Content State',
		CASE zMemory.ZSEARCHINDEXREBUILDSTATE
			WHEN 0 THEN '0-StillTesting Memory-Search Index State-0'
			WHEN 1 THEN '1-StillTesting Memory-Search Index State-1'
			WHEN 2 THEN '2-StillTesting Memory-Search Index State-2'
			ELSE 'Unknown-New-Value!: ' || zMemory.ZSEARCHINDEXREBUILDSTATE || ''
		END AS 'zMemory-Search Index Rebuild State',
		zMemory.ZBLACKLISTEDFEATURE AS 'zMemory-Black Listed Feature',
		zMoment.ZUUID AS 'zMoment-UUID-4TableStart',
		zMoment.ZAGGREGATIONSCORE AS 'zMoment-Aggregation Score',
		DateTime(zMoment.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Start Date',
		DateTime(zMoment.ZREPRESENTATIVEDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Representative Date',
		zMoment.ZTIMEZONEOFFSET AS 'zMoment-Timezone Offset',
		DateTime(zMoment.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-Modification Date',
		DateTime(zMoment.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zMoment-End Date',
		zMoment.ZSUBTITLE AS 'zMoment-SubTitle',
		zMoment.ZTITLE AS 'zMoment-Title',
		CASE zMoment.ZORIGINATORSTATE
			WHEN 0 THEN '0-StillTesting Moment-Originator_State-0'
			WHEN 1 THEN '1-StillTesing Moment-Originator_State-1'
			WHEN 2 THEN '2-StillTesting Moment-Originator_State-2'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZORIGINATORSTATE || ''
		END AS 'zMoment-Originator State',
		CASE zMoment.ZSHARINGCOMPOSITION
			WHEN 0 THEN '0-StillTesting Moment-Sharing_Compo-0'
			WHEN 1 THEN '1-StillTesting Moment-Sharing_Compo-1'
			WHEN 2 THEN '2-StillTesting Moment-Sharing_Compo-2'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZSHARINGCOMPOSITION || ''
		END AS 'zMoment-Sharing Composition',
		zMoment.ZCACHEDCOUNTSHARED AS 'zMoment-Cached Count Shared',
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
			ELSE zMoment.ZGPSHORIZONTALACCURACY
		END AS 'zMoment-GPS Horizontal Accuracy',
		zMoment.ZCACHEDCOUNT AS 'zMoment-Cache Count',
		zMoment.ZCACHEDPHOTOSCOUNT AS 'zMoment-Cached Photos Count',
		zMoment.ZCACHEDVIDEOSCOUNT AS 'zMoment-Cached Videos Count',
		CASE zMoment.ZTRASHEDSTATE
			WHEN 0 THEN 'zMoment Not In Trash-0'
			WHEN 1 THEN 'zMoment In Trash-1'
			ELSE 'Unknown-New-Value!: ' || zMoment.ZTRASHEDSTATE || ''
		END AS 'zMoment-Trashed State',
		SBKAzSugg.ZUUID AS 'SBKAzSugg-UUID-4TableStart',
		SBKAzSugg.ZSUGGESTIONCONTEXT AS 'SBKAzSugg-Suggestion Context',
		SBKAzSugg.ZSHARINGCOMPOSITION AS 'SBKAzSugg-Sharing Composition',
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
		SBKAzSugg.ZACTIONDATA AS 'SBKAzSugg-Action Data',
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
		SBRAzSugg.ZUUID AS 'SBRAzSugg-UUID-4TableStart',
		SBRAzSugg.ZSUGGESTIONCONTEXT AS 'SBRAzSugg-Suggestion Context',
		SBRAzSugg.ZSHARINGCOMPOSITION AS 'SBRAzSugg-Sharing Composition',
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
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZTYPE || ''
		END AS 'SBRAzSugg-Type',
		CASE SBRAzSugg.ZSUBTYPE
			WHEN 501 THEN '501-StillTesting'
			WHEN 502 THEN '502-StillTesting'
			ELSE 'Unknown-New-Value!: ' || SBRAzSugg.ZSUBTYPE || ''
		END AS 'SBRAzSugg-Sub Type',
		SBRAzSugg.ZACTIONDATA AS 'SBRAzSugg-Action Data',
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
		zMedAnlyAstAttr.ZMEDIAANALYSISVERSION AS 'zMedAnlyAstAttr-Media Analysis Version',
		zMedAnlyAstAttr.ZAUDIOCLASSIFICATION AS 'zMedAnlyAstAttr-Audio Classification',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Duration Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTTIMESCALE AS 'zMedAnlyAstAttr-Best Video Range Start Time Scale',
		zMedAnlyAstAttr.ZBESTVIDEORANGEDURATIONVALUE AS 'zMedAnlyAstAttr-Best Video Range Duration Value',
		zMedAnlyAstAttr.ZBESTVIDEORANGESTARTVALUE AS 'zMedAnlyAstAttr-Best Video Range Start Value',
		zMedAnlyAstAttr.ZPACKEDBESTPLAYBACKRECT AS 'zMedAnlyAstAttr-Packed Best Playback Rect',
		zMedAnlyAstAttr.ZACTIVITYSCORE AS 'zMedAnlyAstAttr-Activity Score',
		zMedAnlyAstAttr.ZVIDEOSCORE AS 'zMedAnlyAstAttr-Video Score',
		zMedAnlyAstAttr.ZAUDIOSCORE AS 'zMedAnlyAstAttr-Audio Score',
		zMedAnlyAstAttr.ZWALLPAPERSCORE AS 'zMedAnlyAstAttr-Wallpaper Score',
		zMedAnlyAstAttr.ZAUTOPLAYSUGGESTIONSCORE AS 'zMedAnlyAstAttr-AutoPlay Suggestion Score',
		zMedAnlyAstAttr.ZBLURRINESSSCORE AS 'zMedAnlyAstAttr-Blurriness Score',
		zMedAnlyAstAttr.ZEXPOSURESCORE AS 'zMedAnlyAstAttr-Exposure Score',
		zMedAnlyAstAttr.ZPROBABLEROTATIONDIRECTIONCONFIDENCE AS 'zMedAnlyAstAttr-Probable Rotation Direction Confidence',
		zMedAnlyAstAttr.ZPROBABLEROTATIONDIRECTION AS 'zMedAnlyAstAttr-Probable Rotation Direction',
		zMedAnlyAstAttr.ZSCREENTIMEDEVICEIMAGESENSITIVITY AS 'zMedAnlyAstAttr-Screen Time Device Image Sensitivity',
		zAssetAnalyState.ZASSETUUID AS 'zAssetAnalyState-Asset UUID-4TableStart',
		zAssetAnalyState.ZANALYSISSTATE AS 'zAssetAnalyState-Analyisis State',
		zAssetAnalyState.ZWORKERFLAGS AS 'zAssetAnalyState-Worker Flags',
		zAssetAnalyState.ZWORKERTYPE AS 'zAssetAnalyState-Worker Type',
		DateTime(zAssetAnalyState.ZIGNOREUNTILDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Ignore Until Date',
		DateTime(zAssetAnalyState.ZLASTIGNOREDDATE + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Last Ignored Date',
		DateTime(zAssetAnalyState.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAssetAnalyState-Sort Token',
		zMedAnlyAstAttr.ZCHARACTERRECOGNITIONATTRIBUTES AS 'zMedAnlyAstAttr-Character Recognition Attr',
		zCharRecogAttr.ZALGORITHMVERSION AS 'zCharRecogAttr-Algorithm Version',
		zCharRecogAttr.ZADJUSTMENTVERSION AS 'zCharRecogAttr-Adjustment Version',
		zMedAnlyAstAttr.ZVISUALSEARCHATTRIBUTES AS 'zMedAnlyAstAttr-Visual Search Attributes',
		zVisualSearchAttr.ZALGORITHMVERSION AS 'zVisualSearchAttr-Algorithm Version',
		zVisualSearchAttr.ZADJUSTMENTVERSION AS 'zVisualSearchAttr-Adjustment Version',
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
		zUserFeedback.ZUUID AS 'zUserFeedback-UUID-4TableStart',
		zUserFeedback.ZFEATURE AS 'zUserFeedback-Feature',
		zUserFeedback.ZTYPE AS 'zUserFeedback-Type',
		zUserFeedback.ZLASTMODIFIEDDATE AS 'zUserFeedback-Last Modified Date',
		zUserFeedback.ZCONTEXT AS 'zUserFeedback-Context',
		zUserFeedback.ZCLOUDLOCALSTATE AS 'zUserFeedback-Cloud Local State',
		zUserFeedback.ZCLOUDDELETESTATE AS 'zUserFeedback-Cloud Delete State',
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
		zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zSharePartic_zPK',
		zAsset.ZPHOTOANALYSISATTRIBUTES AS 'zAsset-Photo Analysis Attributes Key',
		zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
		zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
		zAsset.ZMOMENTSHARE AS 'zAsset-Moment Share Key= zShare-zPK',
		zAsset.ZMOMENT AS 'zAsset-zMoment Key= zMoment-zPK',
		zAsset.ZCOMPUTEDATTRIBUTES AS 'zAsset-Computed Attributes Asset Key',
		zAsset.ZHIGHLIGHTBEINGASSETS AS 'zAsset-Highlight Being Assets-HBA Key',
		zAsset.ZHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Highlight Being Extended Assets-HBEA Key',
		zAsset.ZHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Highlight Being Key Asset Private-HBKAP Key',
		zAsset.ZHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Highlight Being Key Asset Shared-HBKAS Key',
		zAsset.ZHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Highligh Being Summary Assets-HBSA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGASSETS AS 'zAsset-Day Group Highlight Being Assets-DGHBA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGEXTENDEDASSETS AS 'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Day Group Highlight Being Key Asset Private-DGHBKAP Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Day Group Highlight Being Key Asset Shared-DGHBKAS Key',
		zAsset.ZDAYGROUPHIGHLIGHTBEINGSUMMARYASSETS AS 'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key',
		zAsset.ZMONTHHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Month Highlight Being Key Asset Private-MHBKAP Key',
		zAsset.ZMONTHHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Month Highlight Being Key Asset Shared-MHBKAS Key',
		zAsset.ZYEARHIGHLIGHTBEINGKEYASSETPRIVATE AS 'zAsset-Year Highlight Being Key Asset Private-YHBKAP Key',
		zAsset.ZYEARHIGHLIGHTBEINGKEYASSETSHARED AS 'zAsset-Year Highlight Being Key Asset Shared-YHBKAS Key',
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
		zAssetContrib.Z_PK AS 'zAsstContrib-zPK',
		zAssetContrib.Z_ENT AS 'zAsstContrib-zEnt',
		zAssetContrib.Z_OPT AS 'zAsstContrib-zOpt',
		zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS AS 'zAsstContrib-3Library Scope Asset Contributors= zAssset-zPK',
		zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
		zAssetDes.Z_PK AS 'zAssetDes-zPK',
		zAssetDes.Z_ENT AS 'zAssetDes-zENT',
		zAssetDes.Z_OPT AS 'zAssetDes-zOPT',
		zAssetDes.ZASSETATTRIBUTES AS 'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK',
		zCharRecogAttr.Z_PK AS 'zCharRecogAttr-zPK',
		zCharRecogAttr.Z_ENT AS 'zCharRecogAttr-zENT',
		zCharRecogAttr.Z_OPT AS 'zCharRecogAttr-zOPT',
		zCharRecogAttr.ZMEDIAANALYSISASSETATTRIBUTES AS 'zCharRecogAttr-MedAssetAttr= zMedAnlyAstAttr-zPK',
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
		zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
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
		zGenAlbum.ZSYNDICATE AS 'zGenAlbum-zSyndicate',
		zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
		SWYConverszGenAlbum.ZUUID AS 'SWYConverszGenAlbum-UUID',
		zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud_GUID = store.cloudphotodb',
		SWYConverszGenAlbum.ZCLOUDGUID AS 'SWYConverszGenAlbum-Cloud GUID',
		zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',
		SWYConverszGenAlbum.ZPROJECTRENDERUUID AS 'SWYConverszGenAlbum-Project Render UUID',
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
		zMemory.Z_PK AS 'zMemory-zPK',
		zMemory.Z_ENT AS 'zMemory-zENT',
		zMemory.Z_OPT AS 'zMemory-zOPT',
		zMemory.ZKEYASSET AS 'zMemory-Key Asset= zAsset-zPK',
		zMemory.ZUUID AS 'zMemory-UUID',
		zMoment.Z_PK AS 'zMoment-zPK',
		zMoment.Z_ENT AS 'zMoment-zENT',
		zMoment.Z_OPT AS 'zMoment-zOPT',
		zMoment.ZHIGHLIGHT AS 'zMoment-Highlight Key',
		zMoment.ZUUID AS 'zMoment-UUID',
		zPerson.Z_PK AS 'zPerson-zPK=zDetFace-Person',
		zPerson.Z_ENT AS 'zPerson-zEnt',
		zPerson.Z_OPT AS 'zPerson-zOpt',
		zPerson.ZSHAREPARTICIPANT AS 'zPerson-Share Participant= zSharePartic-zPK',
		zPerson.ZKEYFACE AS 'zPerson-KeyFace=zDetFace-zPK',
		zPerson.ZASSOCIATEDFACEGROUP AS 'zPerson-Assoc Face Group Key',
		zPerson.ZPERSONUUID AS 'zPerson-Person UUID',
		zPhotoAnalysisAssetAttr.Z_PK AS 'zPhotoAnalysisAssetAttr-zPK',
		zPhotoAnalysisAssetAttr.Z_ENT AS 'zPhotoAnalysisAssetAttr-zEnt',
		zPhotoAnalysisAssetAttr.Z_OPT AS 'zPhotoAnalysisAssetAttr-zOpt',
		zPhotoAnalysisAssetAttr.ZASSET AS 'zPhotoAnalysisAssetAttr-zAsset = zAsset-zPK',
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
		zSharePartic.ZPERSON AS 'zSharePartic-Person= zPerson-zPK',
		zSharePartic.ZUUID AS 'zSharePartic-UUID',
		SBKAzSugg.Z_PK AS 'SBKAzSugg-zPK',
		SBKAzSugg.Z_ENT AS 'SBKAzSugg-zENT',
		SBKAzSugg.Z_OPT AS 'SBKAzSugg-zOPT',
		SBKAzSugg.ZUUID AS 'SBKAzSugg-UUID',
		SBRAzSugg.Z_PK AS 'SBRAzSugg-zPK',
		SBRAzSugg.Z_ENT AS 'SBRAzSugg-zENT',
		SBRAzSugg.Z_OPT AS 'SBRAzSugg-zOPT',
		SBRAzSugg.ZUUID AS 'SBRAzSugg-UUID',
		z3SuggBRA.Z_3REPRESENTATIVEASSETS1 AS 'z3SuggBRA-3RepAssets1',
		z3SuggBRA.Z_58SUGGESTIONSBEINGREPRESENTATIVEASSETS AS 'z3SuggBRA-58SuggBeingRepAssets',
		z3SuggBKA.Z_58SUGGESTIONSBEINGKEYASSETS AS 'z3SuggBKA-58SuggBeingKeyAssets= zSugg-zPK',
		z3SuggBKA.Z_3KEYASSETS AS 'z3SuggBKA-3KeyAssets= zAsset-zPK',
		zUnmAdj.Z_PK AS 'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key',
		zUnmAdj.Z_OPT AS 'zUnmAdj-zOPT',
		zUnmAdj.Z_ENT AS 'zUnmAdj-zENT',
		zUnmAdj.ZASSETATTRIBUTES AS 'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK',
		zUnmAdj.ZUUID AS 'zUnmAdj-UUID',
		zUnmAdj.ZOTHERADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Other Adjustments Fingerprint',
		zUnmAdj.ZSIMILARTOORIGINALADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Similar to Orig Adjustments Fingerprint',
		zUserFeedback.Z_PK AS 'zUserFeedback-zPK',
		zUserFeedback.Z_ENT AS 'zUserFeedback-zENT',
		zUserFeedback.Z_OPT AS 'zUserFeedback-zOPT',
		zUserFeedback.ZPERSON AS 'zUserFeedback-Person= zPerson-zPK',
		zUserFeedback.ZMEMORY AS 'zUserFeedback-Memory= zMemory-zPK',
		zUserFeedback.ZUUID AS 'zUserFeedback-UUID',
		zVisualSearchAttr.Z_PK AS 'zVisualSearchAttr-zPK',
		zVisualSearchAttr.Z_ENT AS 'zVisualSearchAttr-zENT',
		zVisualSearchAttr.Z_OPT AS 'zVisualSearchAttr-zOPT',
		zVisualSearchAttr.ZMEDIAANALYSISASSETATTRIBUTES AS 'zVisualSearchAttr-MedAssetAttr= zMedAnlyAstAttr-zPK',
		z27AlbumLists.Z_27ALBUMS AS 'z27AlbumList-27Albums= zGenAlbum-zPK',
		z27AlbumLists.Z_2ALBUMLISTS AS 'z27AlbumList-Album List Key',
		z27AlbumLists.Z_FOK_27ALBUMS AS 'z27AlbumList-FOK27Albums Key',
		z28Assets.Z_28ALBUMS AS 'z28Assets-28Albums= zGenAlbum-zPK',
		z28Assets.Z_3ASSETS AS 'z28Assets-3Asset Key= zAsset-zPK in the Album',
		z28Assets.Z_FOK_3ASSETS AS 'z28Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY',
		z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AS 'z3MemoryBMCAs-3MovieCuratedAssets= zAsset-zPK',
		z3MemoryBCAs.Z_3CURATEDASSETS AS 'z3MemoryBCAs-3CuratedAssets= zAsset-zPK',
		z3MemoryBCAs.Z_44MEMORIESBEINGCURATEDASSETS AS 'z3MemoryBCAs-44MemoriesBeingCuratedAssets= zMemory-zPK',
		z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-3ExtCuratedAssets= zAsset-zPK',
		z3MemoryBECAs.Z_44MEMORIESBEINGEXTENDEDCURATEDASSETS AS 'z3MemoryBECAs-44MemoriesBeingExtCuratedAssets= zMemory-zPK',
		z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AS 'z3MemoryBRAs-3RepresentativeAssets= zAsset-zPK',
		z3MemoryBRAs.Z_44MEMORIESBEINGREPRESENTATIVEASSETS AS 'z3MemoryBRAs-44RepresentativeAssets= zMemory-zPK',
		z3MemoryBUCAs.Z_3USERCURATEDASSETS AS 'z3MemoryBUCAs-3UserCuratedAssets= zAsset-zPK',
		z3MemoryBUCAs.Z_44MEMORIESBEINGUSERCURATEDASSETS AS 'z3MemoryBUCAs-44MemoriesBeingUserCuratedAssets= zMemory-zPK',
		z3MemoryBCUAs.Z_44MEMORIESBEINGCUSTOMUSERASSETS AS 'z3MemoryBCAs-44Memories Being Custom User Assets',
		z3MemoryBCUAs.Z_3CUSTOMUSERASSETS AS 'z3MemoryBCAs-3Custom User Assets',
		z3MemoryBCUAs.Z_FOK_3CUSTOMUSERASSETS AS 'z3MemoryBCAs-FOK-3Custom User Assets'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZINTERNALRESOURCE zIntResou ON zIntResou.ZASSET = zAsset.Z_PK
			LEFT JOIN ZSCENEPRINT zSceneP ON zSceneP.Z_PK = zAddAssetAttr.ZSCENEPRINT
			LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
			LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
			LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
			LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
			LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
			LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
			LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
			LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDRESOURCE zCldRes ON zCldRes.ZCLOUDMASTER = zCldMast.Z_PK
			LEFT JOIN ZASSETANALYSISSTATE zAssetAnalyState ON zAssetAnalyState.ZASSET = zAsset.Z_PK
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
			LEFT JOIN ZPHOTOANALYSISASSETATTRIBUTES zPhotoAnalysisAssetAttr ON zPhotoAnalysisAssetAttr.ZASSET = zAsset.Z_PK
			LEFT JOIN ZCOMPUTEDASSETATTRIBUTES zCompAssetAttr ON zCompAssetAttr.Z_PK = zAsset.ZCOMPUTEDATTRIBUTES
			LEFT JOIN ZCHARACTERRECOGNITIONATTRIBUTES zCharRecogAttr ON zCharRecogAttr.Z_PK = zMedAnlyAstAttr.ZCHARACTERRECOGNITIONATTRIBUTES
			LEFT JOIN ZVISUALSEARCHATTRIBUTES zVisualSearchAttr ON zVisualSearchAttr.Z_PK = zMedAnlyAstAttr.ZVISUALSEARCHATTRIBUTES
			LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
			LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
			LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
			LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
			LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.ZSHARE = SPLzShare.Z_PK
			LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
			LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
			LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
			LEFT JOIN ZDETECTEDFACE zDetFace ON zAsset.Z_PK = zDetFace.ZASSET
			LEFT JOIN ZPERSON zPerson ON zPerson.Z_PK = zDetFace.ZPERSON
			LEFT JOIN ZDETECTEDFACEPRINT zDetFacePrint ON zDetFacePrint.ZFACE = zDetFace.Z_PK
			LEFT JOIN ZFACECROP zFaceCrop ON zPerson.Z_PK = zFaceCrop.ZPERSON
			LEFT JOIN ZDETECTEDFACEGROUP zDetFaceGroup ON zDetFaceGroup.Z_PK = zDetFace.ZFACEGROUP
			LEFT JOIN Z_3MEMORIESBEINGCURATEDASSETS z3MemoryBCAs ON zAsset.Z_PK = z3MemoryBCAs.Z_3CURATEDASSETS
			LEFT JOIN ZMEMORY zMemory ON z3MemoryBCAs.Z_44MEMORIESBEINGCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGCUSTOMUSERASSETS z3MemoryBCUAs ON zAsset.Z_PK = z3MemoryBCUAs.Z_3CUSTOMUSERASSETS AND z3MemoryBCUAs.Z_44MEMORIESBEINGCUSTOMUSERASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGEXTENDEDCURATEDASSETS z3MemoryBECAs ON zAsset.Z_PK = z3MemoryBECAs.Z_3EXTENDEDCURATEDASSETS AND z3MemoryBECAs.Z_44MEMORIESBEINGEXTENDEDCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGMOVIECURATEDASSETS z3MemoryBMCAs ON zAsset.Z_PK = z3MemoryBMCAs.Z_3MOVIECURATEDASSETS AND z3MemoryBMCAs.Z_44MEMORIESBEINGMOVIECURATEDASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGREPRESENTATIVEASSETS z3MemoryBRAs ON zAsset.Z_PK = z3MemoryBRAs.Z_3REPRESENTATIVEASSETS AND z3MemoryBRAs.Z_44MEMORIESBEINGREPRESENTATIVEASSETS = zMemory.Z_PK
			LEFT JOIN Z_3MEMORIESBEINGUSERCURATEDASSETS z3MemoryBUCAs ON zAsset.Z_PK = z3MemoryBUCAs.Z_3USERCURATEDASSETS AND z3MemoryBUCAs.Z_44MEMORIESBEINGUSERCURATEDASSETS = zMemory.Z_PK
			LEFT JOIN ZUSERFEEDBACK zUserFeedback ON zUserFeedback.ZMEMORY = zMemory.Z_PK
			LEFT JOIN ZMOMENT zMoment ON zMoment.Z_PK = zAsset.ZMOMENT
			LEFT JOIN Z_3SUGGESTIONSBEINGKEYASSETS z3SuggBKA ON z3SuggBKA.Z_3KEYASSETS = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBKAzSugg ON SBKAzSugg.Z_PK = z3SuggBKA.Z_58SUGGESTIONSBEINGKEYASSETS
			LEFT JOIN Z_3SUGGESTIONSBEINGREPRESENTATIVEASSETS z3SuggBRA ON z3SuggBRA.Z_3REPRESENTATIVEASSETS1 = zAsset.Z_PK
			LEFT JOIN ZSUGGESTION SBRAzSugg ON SBRAzSugg.Z_PK = z3SuggBRA.Z_58SUGGESTIONSBEINGREPRESENTATIVEASSETS
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
							row[1080], row[1081], row[1082]))

		data_headers = (('zAsset-Added Date-0', 'datetime'),
						'zAsset- SortToken -CameraRoll-1',
						'zAsset Complete-2',
						'zAsset-zPK-4QueryStart-3',
						'zAddAssetAttr-zPK-4QueryStart-4',
						'zAsset-UUID = store.cloudphotodb-4QueryStart-5',
						'zAddAssetAttr-Master Fingerprint-4TableStart-6',
						'zIntResou-Fingerprint-4TableStart-7',
						'zAsset-Bundle Scope-8',
						'zAsset-Syndication State-9',
						'zAsset-Cloud is My Asset-10',
						'zAsset-Cloud is deletable-Asset-11',
						'zAsset-Cloud_Local_State-12',
						'zAsset-Visibility State-13',
						'zExtAttr-Camera Make-14',
						'zExtAttr-Camera Model-15',
						'zExtAttr-Lens Model-16',
						'zExtAttr-Flash Fired-17',
						'zExtAttr-Focal Lenght-18',
						'zExtAttr-Focal Lenth in 35MM-19',
						'zExtAttr-Digital Zoom Ratio-20',
						'zAsset-Derived Camera Capture Device-21',
						'zAddAssetAttr-Camera Captured Device-22',
						'zAddAssetAttr-Imported by-23',
						'zCldMast-Imported By-24',
						'zAddAssetAttr.Imported by Bundle Identifier-25',
						'zAddAssetAttr-Imported By Display Name-26',
						'zCldMast-Imported by Bundle ID-27',
						'zCldMast-Imported by Display Name-28',
						'zAsset-Saved Asset Type-29',
						'zAsset-Directory-Path-30',
						'zAsset-Filename-31',
						'zAddAssetAttr- Original Filename-32',
						'zCldMast- Original Filename-33',
						'zAddAssetAttr- Syndication Identifier-SWY-Files-34',
						'zAsset-Active Library Scope Participation State -4QueryStart-35',
						'zAsset-Library Scope Share State- StillTesting -4QueryStart-36',
						'zShare-Cloud Photo Count-SPL -4QueryStart-37',
						'zShare-Cloud Video Count-SPL -4QueryStart-38',
						('zAddAssetAttr-Date Created Source-39', 'datetime'),
						('zAsset-Date Created-40', 'datetime'),
						('zCldMast-Creation Date-41', 'datetime'),
						('zIntResou-CldMst Date Created-42', 'datetime'),
						'zAddAssetAttr-Time Zone Name-43',
						'zAddAssetAttr-Time Zone Offset-44',
						'zAddAssetAttr-Inferred Time Zone Offset-45',
						'zAddAssetAttr-EXIF-String-46',
						('zAsset-Modification Date-47', 'datetime'),
						('zAsset-Last Shared Date-48', 'datetime'),
						'zCldMast-Cloud Local State-49',
						('zCldMast-Import Date-50', 'datetime'),
						('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-51', 'datetime'),
						'zAddAssetAttr-Import Session ID-4QueryStart-52',
						('zAddAssetAttr-Alt Import Image Date-53', 'datetime'),
						'zCldMast-Import Session ID- AirDrop-StillTesting- 4QueryStart-54',
						('zAsset-Cloud Batch Publish Date-55', 'datetime'),
						('zAsset-Cloud Server Publish Date-56', 'datetime'),
						'zAsset-Cloud Download Requests-57',
						'zAsset-Cloud Batch ID-58',
						'zAddAssetAttr-Upload Attempts-59',
						'zAsset-Latitude-60',
						'zExtAttr-Latitude-61',
						'zAsset-Longitude-62',
						'zExtAttr-Longitude-63',
						'zAddAssetAttr-GPS Horizontal Accuracy-64',
						'zAddAssetAttr-Location Hash-65',
						'zAddAssetAttr-Shifted Location Valid-66',
						'zAddAssetAttr-Shifted Location Data-67',
						'zAddAssetAttr-Reverse Location Is Valid-68',
						'zAddAssetAttr-Reverse Location Data-69',
						'ParentzGenAlbum-UUID-4QueryStart-70',
						'zGenAlbum-UUID-4QueryStart-71',
						'SWYConverszGenAlbum-UUID-4QueryStart-72',
						'ParentzGenAlbum-Cloud GUID-4QueryStart-73',
						'zGenAlbum-Cloud GUID-4QueryStart-74',
						'SWYConverszGenAlbum-Cloud GUID-4QueryStart-75',
						'zCldShareAlbumInvRec-Album GUID-4QueryStart-76',
						'zCldShareAlbumInvRec-Cloud GUID-4QueryStart-77',
						'zGenAlbum-Project Render UUID-4QueryStart-78',
						'SWYConverszGenAlbum-Project Render UUID-4QueryStart-79',
						'ParentzGenAlbum-Cloud-Local-State-4QueryStart-80',
						'zGenAlbum-Cloud_Local_State-4QueryStart-81',
						'SWYConverszGenAlbum-Cloud_Local_State-4QueryStart-82',
						('ParentzGenAlbum- Creation Date- 4QueryStart-83', 'datetime'),
						('zGenAlbum- Creation Date- 4QueryStart-84', 'datetime'),
						('SWYConverszGenAlbum- Creation Date- 4QueryStart-85', 'datetime'),
						('zGenAlbum- Cloud Creation Date- 4QueryStart-86', 'datetime'),
						('SWYConverszGenAlbum- Cloud Creation Date- 4QueryStart-87', 'datetime'),
						('zGenAlbum- Start Date- 4QueryStart-88', 'datetime'),
						('SWYConverszGenAlbum- Start Date- 4QueryStart-89', 'datetime'),
						('zGenAlbum- End Date- 4QueryStart-90', 'datetime'),
						('SWYConverszGenAlbum- End Date- 4QueryStart-91', 'datetime'),
						('zGenAlbum-Cloud Subscription Date- 4QueryStart-92', 'datetime'),
						('SWYConverszGenAlbum-Cloud Subscription Date- 4QueryStart-93', 'datetime'),
						'ParentzGenAlbum- Title- 4QueryStart-94',
						'zGenAlbum- Title-User&System Applied- 4QueryStart-95',
						'SWYConverszGenAlbum- Title -User&System Applied- 4QueryStart-96',
						'zGenAlbum-Import Session ID-SWY- 4QueryStart-97',
						'zAsset- Conversation= zGenAlbum_zPK -4QueryStart-98',
						'SWYConverszGenAlbum- Import Session ID-SWY- 4QueryStart-99',
						'zGenAlbum-Imported by Bundle Identifier- 4QueryStart-100',
						'SWYzGenAlbum-Imported by Bundle Identifier- 4QueryStart-101',
						'SWYConverszGenAlbum- Syndicate-4QueryStart-102',
						'zGenAlbum-zENT- Entity- 4QueryStart-103',
						'ParentzGenAlbum- Kind- 4QueryStart-104',
						'zGenAlbum-Album Kind- 4QueryStart-105',
						'SWYConverszGenAlbum-Album Kind- 4QueryStart-106',
						'AAAzCldMastMedData-zOPT-107',
						'zAddAssetAttr-Media Metadata Type-108',
						'AAAzCldMastMedData-Data-109',
						'CldMasterzCldMastMedData-zOPT-110',
						'zCldMast-Media Metadata Type-111',
						'CMzCldMastMedData-Data-112',
						'zAsset-Search Index Rebuild State-113',
						'zAddAssetAttr-Syndication History-114',
						'zMedAnlyAstAttr-Syndication Processing Version-115',
						'zMedAnlyAstAttr-Syndication Processing Value-116',
						'zAsset-Orientation-117',
						'zAddAssetAttr-Original Orientation-118',
						'zAsset-Kind-119',
						'zAsset-Kind-Sub-Type-120',
						'zAddAssetAttr-Cloud Kind Sub Type-121',
						'zAsset-Playback Style-122',
						'zAsset-Playback Variation-123',
						'zAsset-Video Duration-124',
						'zExtAttr-Duration-125',
						'zAsset-Video CP Duration-126',
						'zAddAssetAttr-Video CP Duration Time Scale-127',
						'zAsset-Video CP Visibility State-128',
						'zAddAssetAttr-Video CP Display Value-129',
						'zAddAssetAttr-Video CP Display Time Scale-130',
						'zIntResou-Datastore Class ID-131',
						'zAsset-Cloud Placeholder Kind-132',
						'zIntResou-Local Availability-133',
						'zIntResou-Local Availability Target-134',
						'zIntResou-Cloud Local State-135',
						'zIntResou-Remote Availability-136',
						'zIntResou-Remote Availability Target-137',
						'zIntResou-Transient Cloud Master-138',
						'zIntResou-Side Car Index-139',
						'zIntResou- File ID-140',
						'zIntResou-Version-141',
						'zAddAssetAttr- Original-File-Size-142',
						'zIntResou-Resource Type-143',
						'zIntResou-Datastore Sub-Type-144',
						'zIntResou-Cloud Source Type-145',
						'zIntResou-Data Length-146',
						'zIntResou-Recipe ID-147',
						('zIntResou-Cloud Last Prefetch Date-148', 'datetime'),
						'zIntResou-Cloud Prefetch Count-149',
						('zIntResou- Cloud-Last-OnDemand Download-Date-150', 'datetime'),
						'zIntResou-UniformTypeID_UTI_Conformance_Hint-151',
						'zIntResou-Compact-UTI-152',
						'zAsset-Uniform Type ID-153',
						'zAsset-Original Color Space-154',
						'zCldMast-Uniform_Type_ID-155',
						'zCldMast-Full Size JPEG Source-156',
						'zAsset-HDR Gain-157',
						'zAsset-zHDR_Type-158',
						'zExtAttr-Codec-159',
						'zIntResou-Codec Four Char Code Name-160',
						'zCldMast-Codec Name-161',
						'zCldMast-Video Frame Rate-162',
						'zCldMast-Placeholder State-163',
						'zAsset-Depth_Type-164',
						'zAsset-Avalanche UUID-4TableStart-165',
						'zAsset-Avalanche_Pick_Type-BurstAsset-166',
						'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-167',
						'zAddAssetAttr-Cloud Recovery State-168',
						'zAddAssetAttr-Cloud State Recovery Attempts Count-169',
						'zAsset-Deferred Processing Needed-170',
						'zAsset-Video Deferred Processing Needed-171',
						'zAddAssetAttr-Deferred Photo Identifier-4QueryStart-172',
						'zAddAssetAttr-Deferred Processing Candidate Options-173',
						'zAsset-Has Adjustments-Camera-Effects-Filters-174',
						'zUnmAdj-UUID-4TableStart-175',
						'zAsset-Adjustment Timestamp-176',
						'zUnmAdj-Adjustment Timestamp-177',
						'zAddAssetAttr-Editor Bundle ID-178',
						'zUnmAdj-Editor Localized Name-179',
						'zUnmAdj-Adjustment Format ID-180',
						'zAddAssetAttr-Montage-181',
						'zUnmAdj-Adjustment Render Types-182',
						'zUnmAdj-Adjustment Format Version-183',
						'zUnmAdj-Adjustment Base Image Format-184',
						'zAsset-Favorite-185',
						'zAsset-Hidden-186',
						'zAsset-Trashed State-LocalAssetRecentlyDeleted-187',
						('zAsset-Trashed Date-188', 'datetime'),
						'zAsset-Trashed by Participant= zSharePartic_zPK-4QueryStart-189',
						'zAsset-Delete-Reason-190',
						'zIntResou-Trash State-191',
						('zIntResou-Trashed Date-192', 'datetime'),
						'zAsset-Cloud Delete State-193',
						'zIntResou-Cloud Delete State-194',
						'zAddAssetAttr-PTP Trashed State-195',
						'zIntResou-PTP Trashed State-196',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-4TableStart-197',
						'zMedAnlyAstAttr-Media Analysis Timestamp-198',
						('zAsset-Analysis State Modification Date-199', 'datetime'),
						'zAddAssetAttr- Pending View Count-200',
						'zAddAssetAttr- View Count-201',
						'zAddAssetAttr- Pending Play Count-202',
						'zAddAssetAttr- Play Count-203',
						'zAddAssetAttr- Pending Share Count-204',
						'zAddAssetAttr- Share Count-205',
						'zAddAssetAttr-Allowed for Analysis-206',
						'zAddAssetAttr-Scene Analysis Version-207',
						'zAddAssetAttr-Scene Analysis is From Preview-208',
						'zAddAssetAttr-Scene Analysis Timestamp-209',
						'zAsset-Duplication Asset Visibility State-210',
						'zAddAssetAttr-Destination Asset Copy State-211',
						'zAddAssetAttr-Duplicate Detector Perceptual Processing State-212',
						'zAddAssetAttr-Source Asset for Duplication Scope ID-213',
						'zCldMast-Source Master For Duplication Scope ID-214',
						'zAddAssetAttr-Source Asset For Duplication ID-215',
						'zCldMast-Source Master for Duplication ID-216',
						'zAddAssetAttr-Variation Suggestions States-217',
						'zAsset-High Frame Rate State-218',
						'zAsset-Video Key Frame Time Scale-219',
						'zAsset-Video Key Frame Value-220',
						'zExtAttr-ISO-221',
						'zExtAttr-Metering Mode-222',
						'zExtAttr-Sample Rate-223',
						'zExtAttr-Track Format-224',
						'zExtAttr-White Balance-225',
						'zExtAttr-Aperture-226',
						'zExtAttr-BitRate-227',
						'zExtAttr-Exposure Bias-228',
						'zExtAttr-Frames Per Second-229',
						'zExtAttr-Shutter Speed-230',
						'zExtAttr-Slush Scene Bias-231',
						'zExtAttr-Slush Version-232',
						'zExtAttr-Slush Preset-233',
						'zExtAttr-Slush Warm Bias-234',
						'zAsset-Height-235',
						'zAddAssetAttr-Original Height-236',
						'zIntResou-Unoriented Height-237',
						'zAsset-Width-238',
						'zAddAssetAttr-Original Width-239',
						'zIntResou-Unoriented Width-240',
						'zShare-Thumbnail Image Data-241',
						'SPLzShare-Thumbnail Image Data-242',
						'zAsset-Thumbnail Index-243',
						'zAddAssetAttr-Embedded Thumbnail Height-244',
						'zAddAssetAttr-Embedded Thumbnail Length-245',
						'zAddAssetAttr-Embedded Thumbnail Offset-246',
						'zAddAssetAttr-Embedded Thumbnail Width-247',
						'zAsset-Packed Acceptable Crop Rect-248',
						'zAsset-Packed Badge Attributes-249',
						'zAsset-Packed Preferred Crop Rect-250',
						'zAsset-Curation Score-251',
						'zAsset-Camera Processing Adjustment State-252',
						'zAsset-Depth Type-253',
						'zAsset-Is Magic Carpet-QuicktimeMOVfile-254',
						'zAddAssetAttr-Orig Resource Choice-255',
						'zAddAssetAttr-Spatial Over Capture Group ID-256',
						'zAddAssetAttr-Place Annotation Data-257',
						'zAddAssetAttr-Distance Identity-258',
						'zAddAssetAttr-Edited IPTC Attributes-259',
						'zAssetDes-Long Description-260',
						'zAddAssetAttr-Asset Description-261',
						'zAddAssetAttr-Title-Comments via Cloud Website-262',
						'zAddAssetAttr-Accessibility Description-263',
						'zAddAssetAttr-Photo Stream Tag ID-264',
						'zPhotoAnalysisAssetAttr-Wallpaper Properties Version-265',
						'zPhotoAnalysisAssetAttr-Wallpaper Properties Timestamp-266',
						('zCldFeedEnt-Entry Date-267', 'datetime'),
						'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-268',
						'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-269',
						'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-270',
						'zCldFeedEnt-Entry Priority Number-271',
						'zCldFeedEnt-Entry Type Number-272',
						'zCldSharedComment-Cloud GUID-4TableStart-273',
						('zCldSharedComment-Date-274', 'datetime'),
						('zCldSharedComment-Comment Client Date-275', 'datetime'),
						('zAsset-Cloud Last Viewed Comment Date-276', 'datetime'),
						'zCldSharedComment-Type-277',
						'zCldSharedComment-Comment Text-278',
						'zCldSharedComment-Commenter Hashed Person ID-279',
						'zCldSharedComment-Batch Comment-280',
						'zCldSharedComment-Is a Caption-281',
						'zAsset-Cloud Has Comments by Me-282',
						'zCldSharedComment-Is My Comment-283',
						'zCldSharedComment-Is Deletable-284',
						'zAsset-Cloud Has Comments Conversation-285',
						'zAsset-Cloud Has Unseen Comments-286',
						'zCldSharedComment-Liked-287',
						'zAddAssetAttr-Share Type-288',
						'zAsset-Library Scope Share State- StillTesting-289',
						'zAsset-Active Library Scope Participation State-290',
						'zAddAssetAttr-Library Scope Asset Contributors To Update-291',
						'zShare-UUID-CMM-4TableStart-292',
						'SPLzShare-UUID-SPL-4TableStart-293',
						'zShare-zENT-CMM-294',
						'SPLzShare-zENT-SPL-295',
						'zSharePartic-z54SHARE-296',
						'SPLzSharePartic-z54SHARE-297',
						'zShare-Status-CMM-298',
						'SPLzShare-Status-SPL-299',
						'zShare-Scope Type-CMM-300',
						'SPLzShare-Scope Type-SPL-301',
						'zShare-Local Publish State-CMM-302',
						'SPLzShare-Local Publish State-SPL-303',
						'zShare-Public Permission-CMM-304',
						'SPLzShare-Public Permission-SPL-305',
						'zShare-Originating Scope ID-CMM-306',
						'SPLzShare-Originating Scope ID-SPL-307',
						'zShare-Scope ID-CMM-308',
						'SPLzShare-Scope ID-SPL-309',
						'zShare-Title-CMM-310',
						'SPLzShare-Title-SPL-311',
						'zShare-Share URL-CMM-312',
						'SPLzShare-Share URL-SPL-313',
						('zShare-Creation Date-CMM-314', 'datetime'),
						('SPLzShare-Creation Date-SPL-315', 'datetime'),
						('zShare-Start Date-CMM-316', 'datetime'),
						('SPLzShare-Start Date-SPL-317', 'datetime'),
						('zShare-End Date-CMM-318', 'datetime'),
						('SPLzShare-End Date-SPL-319', 'datetime'),
						('zShare-Expiry Date-CMM-320', 'datetime'),
						('SPLzShare-Expiry Date-SPL-321', 'datetime'),
						'zShare-Cloud Item Count-CMM-322',
						'SPLzShare-Cloud Item Count-SPL-323',
						'zShare-Asset Count-CMM-324',
						'SPLzShare-Asset Count-SPL-325',
						'zShare-Cloud Photo Count-CMM-326',
						'SPLzShare-Cloud Photo Count-SPL-327',
						'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-CMM-328',
						'SPLzShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-SPL-329',
						'zShare-Photos Count-CMM-330',
						'SPLzShare-Photos Count-CMM-SPL-331',
						'zShare-Uploaded Photos Count-CMM-332',
						'SPLzShare-Uploaded Photos Count-SPL-333',
						'zShare-Cloud Video Count-CMM-334',
						'SPLzShare-Cloud Video Count-SPL-335',
						'zShare-Videos Count-CMM-336',
						'SPLzShare-Videos Count-SPL-337',
						'zShare-Uploaded Videos Count-CMM-338',
						'SPLzShare-Uploaded Videos Count-SPL-339',
						'zShare-Force Sync Attempted-CMM-340',
						'SPLzShare-Force Sync Attempted-SPL-341',
						'zShare-Cloud Local State-CMM-342',
						'SPLzShare-Cloud Local State-SPL-343',
						'zShare-Scope Syncing State-CMM-344',
						'SPLzShare-Scope Syncing State-SPL-345',
						'zShare-Auto Share Policy-CMM-346',
						'SPLzShare-Auto Share Policy-SPL-347',
						'zShare-Should Notify On Upload Completion-CMM-348',
						'SPLzShare-Should Notify On Upload Completion-SPL-349',
						'zAsset-Trashed by Participant= zSharePartic_zPK-SPL-CMM-350',
						'zShare-Trashed State-CMM-351',
						'SPLzShare-Trashed State-SPL-352',
						'zShare-Cloud Delete State-CMM-353',
						'SPLzShare-Cloud Delete State-SPL-354',
						('zShare-Trashed Date-CMM-355', 'datetime'),
						('SPLzShare-Trashed Date-SPL-356', 'datetime'),
						('zShare-LastParticipant Asset Trash Notification Date-CMM-357', 'datetime'),
						('SPLzShare-LastParticipant Asset Trash Notification Date-SPL-358', 'datetime'),
						('zShare-Last Participant Asset Trash Notification View Date-CMM-359', 'datetime'),
						('SPLzShare-Last Participant Asset Trash Notification View Date-SPL-360', 'datetime'),
						'zShare-Exit Source-CMM-361',
						'SPLzShare-Exit Source-SPL-362',
						'zShare-SPL_Exit State-CMM-363',
						'SPLzShare-SPL_Exit State-SPL-364',
						'zShare-Exit Type-CMM-365',
						'SPLzShare-Exit Type-SPL-366',
						'zShare-Should Ignor Budgets-CMM-367',
						'SPLzShare-Should Ignor Budgets-SPL-368',
						'zShare-Preview State-CMM-369',
						'SPLzShare-Preview State-SPL-370',
						'zShare-Preview Data-CMM-371',
						'SPLzShare-Preview Data-SPL-372',
						'zShare-Rules-CMM-373',
						'SPLzShare-Rules-SPL-374',
						'zShare-Thumbnail Image Data-CMM-375',
						'SPLzShare-Thumbnail Image Data-SPL-376',
						'zShare-Participant Cloud Update State-CMM-377',
						'SPLzShare-Participant Cloud Update State-SPL-378',
						'zSharePartic-UUID-4TableStart-379',
						'SPLzSharePartic-UUID-4TableStart-380',
						'zSharePartic-Acceptance Status-381',
						'SPLzSharePartic-Acceptance Status-382',
						'zSharePartic-Is Current User-383',
						'SPLzSharePartic-Is Current User-384',
						'zSharePartic-Role-385',
						'SPLzSharePartic-Role-386',
						'zSharePartic-Premission-387',
						'SPLzSharePartic-Premission-388',
						'zSharePartic-Participant ID-389',
						'SPLzSharePartic-Participant ID-390',
						'zSharePartic-User ID-391',
						'SPLzSharePartic-User ID-392',
						'zAsstContrib-Participant= zSharePartic-zPK-4TableStart-393',
						'SPLzSharePartic-zPK-4TableStart-394',
						'zSharePartic-zPK-4TableStart-395',
						'zSharePartic-Email Address-396',
						'SPLzSharePartic-Email Address-397',
						'zSharePartic-Phone Number-398',
						'SPLzSharePartic-Phone Number-399',
						'zSharePartic-Exit State-400',
						'SPLzSharePartic-Exit State-401',
						'ParentzGenAlbum-UUID-4TableStart-402',
						'zGenAlbum-UUID-4TableStart-403',
						'SWYConverszGenAlbum-UUID-4TableStart-404',
						'ParentzGenAlbum-Cloud GUID-4TableStart-405',
						'zGenAlbum-Cloud GUID-4TableStart-406',
						'SWYConverszGenAlbum-Cloud GUID-4TableStart-407',
						'zCldShareAlbumInvRec-Album GUID-4TableStart-408',
						'zCldShareAlbumInvRec-Cloud GUID-4TableStart-409',
						'zGenAlbum-Project Render UUID-4TableStart-410',
						'SWYConverszGenAlbum-Project Render UUID-4TableStart-411',
						'zAlbumList-Needs Reordering Number-412',
						'zGenAlbum-zENT- Entity-413',
						'ParentzGenAlbum-Kind-414',
						'zGenAlbum-Album Kind-415',
						'SWYConverszGenAlbum-Album Kind-416',
						'ParentzGenAlbum-Cloud-Local-State-417',
						'zGenAlbum-Cloud_Local_State-418',
						'SWYConverszGenAlbum-Cloud_Local_State-419',
						'ParentzGenAlbum- Title-420',
						'zGenAlbum- Title-User&System Applied-421',
						'SWYConverszGenAlbum- Title -User&System Applied-422',
						'zGenAlbum-Import Session ID-SWY-423',
						'zAsset- Conversation= zGenAlbum_zPK-424',
						'SWYConverszGenAlbum- Import Session ID-SWY-425',
						'zGenAlbum-Imported by Bundle Identifier-426',
						'SWYzGenAlbum-Imported by Bundle Identifier-427',
						'SWYConverszGenAlbum- Syndicate-428',
						('ParentzGenAlbum-Creation Date-429', 'datetime'),
						('zGenAlbum-Creation Date-430', 'datetime'),
						('SWYConverszGenAlbum-Creation Date-431', 'datetime'),
						('zGenAlbum-Cloud Creation Date-432', 'datetime'),
						('SWYConverszGenAlbum-Cloud Creation Date-433', 'datetime'),
						('zGenAlbum-Start Date-434', 'datetime'),
						('SWYConverszGenAlbum-Start Date-435', 'datetime'),
						('zGenAlbum-End Date-436', 'datetime'),
						('SWYConverszGenAlbum-End Date-437', 'datetime'),
						('zGenAlbum-Cloud Subscription Date-438', 'datetime'),
						('SWYConverszGenAlbum-Cloud Subscription Date-439', 'datetime'),
						'ParentzGenAlbum-Pending Items Count-440',
						'zGenAlbum-Pending Items Count-441',
						'SWYConverszGenAlbum-Pending Items Count-442',
						'ParentzGenAlbum-Pending Items Type-443',
						'zGenAlbum-Pending Items Type-444',
						'SWYConverszGenAlbum-Pending Items Type-445',
						'zGenAlbum- Cached Photos Count-446',
						'SWYConverszGenAlbum- Cached Photos Count-447',
						'zGenAlbum- Cached Videos Count-448',
						'SWYConverszGenAlbum- Cached Videos Count-449',
						'zGenAlbum- Cached Count-450',
						'SWYConverszGenAlbum- Cached Count-451',
						'ParentzGenAlbum-Sync Event Order Key-452',
						'zGenAlbum-Sync Event Order Key-453',
						'SWYConverszGenAlbum-Sync Event Order Key-454',
						'zGenAlbum-Has Unseen Content-455',
						'SWYConverszGenAlbum-Has Unseen Content-456',
						'zGenAlbum-Unseen Asset Count-457',
						'SWYConverszGenAlbum-Unseen Asset Count-458',
						'zGenAlbum-is Owned-459',
						'SWYConverszGenAlbum-is Owned-460',
						'zGenAlbum-Cloud Relationship State-461',
						'SWYConverszGenAlbum-Cloud Relationship State-462',
						'zGenAlbum-Cloud Relationship State Local-463',
						'SWYConverszGenAlbum-Cloud Relationship State Local-464',
						'zGenAlbum-Cloud Owner Mail Key-465',
						'SWYConverszGenAlbum-Cloud Owner Mail Key-466',
						'zGenAlbum-Cloud Owner Frist Name-467',
						'SWYConverszGenAlbum-Cloud Owner Frist Name-468',
						'zGenAlbum-Cloud Owner Last Name-469',
						'SWYConverszGenAlbum-Cloud Owner Last Name-470',
						'zGenAlbum-Cloud Owner Full Name-471',
						'SWYConverszGenAlbum-Cloud Owner Full Name-472',
						'zGenAlbum-Cloud Person ID-473',
						'SWYConverszGenAlbum-Cloud Person ID-474',
						'zAsset-Cloud Owner Hashed Person ID-475',
						'zGenAlbum-Cloud Owner Hashed Person ID-476',
						'SWYConverszGenAlbum-Cloud Owner Hashed Person ID-477',
						'zGenAlbum-Local Cloud Multi-Contributors Enabled-478',
						'SWYConverszGenAlbum-Local Cloud Multi-Contributors Enabled-479',
						'zGenAlbum-Cloud Multi-Contributors Enabled-480',
						'SWYConverszGenAlbum-Cloud Multi-Contributors Enabled-481',
						'zGenAlbum-Cloud Album Sub Type-482',
						'SWYConverszGenAlbum-Cloud Album Sub Type-483',
						('zGenAlbum-Cloud Contribution Date-484', 'datetime'),
						('SWYConverszGenAlbum-Cloud Contribution Date-485', 'datetime'),
						('zGenAlbum-Cloud Last Interesting Change Date-486', 'datetime'),
						('SWYConverszGenAlbum-Cloud Last Interesting Change Date-487', 'datetime'),
						'zGenAlbum-Cloud Notification Enabled-488',
						'SWYConverszGenAlbum-Cloud Notification Enabled-489',
						'ParentzGenAlbum-Pinned-490',
						'zGenAlbum-Pinned-491',
						'SWYConverszGenAlbum-Pinned-492',
						'ParentzGenAlbum-Custom Sort Key-493',
						'zGenAlbum-Custom Sort Key-494',
						'SWYConverszGenAlbum-Custom Sort Key-495',
						'ParentzGenAlbum-Custom Sort Ascending-496',
						'zGenAlbum-Custom Sort Ascending-497',
						'SWYConverszGenAlbum-Custom Sort Ascending-498',
						'ParentzGenAlbum-Is Prototype-499',
						'zGenAlbum-Is Prototype-500',
						'SWYConverszGenAlbum-Is Prototype-501',
						'ParentzGenAlbum-Project Document Type-502',
						'zGenAlbum-Project Document Type-503',
						'SWYConverszGenAlbum-Project Document Type-504',
						'ParentzGenAlbum-Custom Query Type-505',
						'zGenAlbum-Custom Query Type-506',
						'SWYConverszGenAlbum-Custom Query Type-507',
						'ParentzGenAlbum-Trashed State-508',
						('ParentzGenAlbum-Trash Date-509', 'datetime'),
						'zGenAlbum-Trashed State-510',
						('zGenAlbum-Trash Date-511', 'datetime'),
						'SWYConverszGenAlbum-Trashed State-512',
						('SWYConverszGenAlbum-Trash Date-513', 'datetime'),
						'ParentzGenAlbum-Cloud Delete State-514',
						'zGenAlbum-Cloud Delete State-515',
						'SWYConverszGenAlbum-Cloud Delete State-516',
						'zGenAlbum-Cloud Owner Whitelisted-517',
						'SWYConverszGenAlbum-Cloud Owner Whitelisted-518',
						'zGenAlbum-Cloud Local Public URL Enabled-519',
						'SWYConverszGenAlbum-Cloud Local Public URL Enabled-520',
						'zGenAlbum-Cloud Public URL Enabled-521',
						'zGenAlbum-Public URL-522',
						'SWYConverszGenAlbum-Cloud Public URL Enabled-523',
						'SWYConverszGenAlbum-Public URL-524',
						'zGenAlbum-Key Asset Face Thumb Index-525',
						'SWYConverszGenAlbum-Key Asset Face Thumb Index-526',
						'zGenAlbum-Project Text Extension ID-527',
						'SWYConverszGenAlbum-Project Text Extension ID-528',
						'zGenAlbum-User Query Data-529',
						'SWYConverszGenAlbum-User Query Data-530',
						'zGenAlbum-Custom Query Parameters-531',
						'SWYConverszGenAlbum-Custom Query Parameters-532',
						'zGenAlbum-Project Data-533',
						'SWYConverszGenAlbum-Project Data-534',
						'zGenAlbum-Search Index Rebuild State-535',
						'SWYConverszGenAlbum-Search Index Rebuild State-536',
						'zGenAlbum-Duplicate Type-537',
						'SWYConverszGenAlbum-Duplicate Type-538',
						'zGenAlbum-Privacy State-539',
						'SWYConverszGenAlbum-Privacy State-540',
						'zCldShareAlbumInvRec-zUUID-4TableStart-541',
						'zCldShareAlbumInvRec-Is My Invitation to Shared Album-542',
						'zCldShareAlbumInvRec-Invitation State Local-543',
						'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-544',
						('zCldShareAlbumInvRec-Subscription Date-545', 'datetime'),
						'zCldShareAlbumInvRec-Invitee First Name-546',
						'zCldShareAlbumInvRec-Invitee Last Name-547',
						'zCldShareAlbumInvRec-Invitee Full Name-548',
						'zCldShareAlbumInvRec-Invitee Hashed Person ID-549',
						'zCldShareAlbumInvRec-Invitee Email Key-550',
						'zGenAlbum-Key Asset Face ID-551',
						'zFaceCrop-Face Area Points-552',
						'zAsset-Face Adjustment Version-553',
						'zAddAssetAttr-Face Analysis Version-554',
						'zDetFace-Asset Visible-555',
						'zPerson-Face Count-556',
						'zDetFace-Face Crop-557',
						'zDetFace-Face Algorithm Version-558',
						'zDetFace-Adjustment Version-559',
						'zDetFace-UUID-4TableStart-560',
						'zPerson-Person UUID-4TableStart-561',
						'zDetFace-Confirmed Face Crop Generation State-562',
						'zDetFace-Manual-563',
						'zDetFace-Detection Type-564',
						'zPerson-Detection Type-565',
						'zDetFace-VIP Model Type-566',
						'zDetFace-Name Source-567',
						'zDetFace-Cloud Name Source-568',
						'zPerson-Merge Candidate Confidence-569',
						'zPerson-Person URI-570',
						'zPerson-Display Name-571',
						'zPerson-Full Name-572',
						'zPerson-Cloud Verified Type-573',
						'zFaceCrop-State-574',
						'zFaceCrop-Type-575',
						'zFaceCrop-UUID-4TableStart-576',
						'zPerson-Type-577',
						'zPerson-Verified Type-578',
						'zPerson-Gender Type-579',
						'zDetFace-Gender Type-580',
						'zDetFace-Center X-581',
						'zDetFace-Center Y-582',
						'zPerson-Age Type Estimate-583',
						'zDetFace-Age Type Estimate-584',
						'zDetFace-Ethnicity Type-585',
						'zDetFace-Skin Tone Type-586',
						'zDetFace-Hair Type-587',
						'zDetFace-Hair Color Type-588',
						'zDetFace-Head Gear Type-589',
						'zDetFace-Facial Hair Type-590',
						'zDetFace-Has Face Mask-591',
						'zDetFace-Pose Type-592',
						'zDetFace-Face Expression Type-593',
						'zDetFace-Has Smile-594',
						'zDetFace-Smile Type-595',
						'zDetFace-Lip Makeup Type-596',
						'zDetFace-Eyes State-597',
						'zDetFace-Is Left Eye Closed-598',
						'zDetFace-Is Right Eye Closed-599',
						'zDetFace-Gaze Center X-600',
						'zDetFace-Gaze Center Y-601',
						'zDetFace-Face Gaze Type-602',
						'zDetFace-Eye Glasses Type-603',
						'zDetFace-Eye Makeup Type-604',
						'zDetFace-Cluster Squence Number Key-605',
						'zDetFace-Grouping ID-606',
						'zDetFace-Master ID-607',
						'zDetFace-Quality-608',
						'zDetFace-Quality Measure-609',
						'zDetFace-Source Height-610',
						'zDetFace-Source Width-611',
						'zDetFace-Hidden-Asset Hidden-612',
						'zDetFace-In Trash-Recently Deleted-613',
						'zDetFace-Cloud Local State-614',
						'zDetFace-Training Type-615',
						'zDetFace.Pose Yaw-616',
						'zDetFace-Body Center X-617',
						'zDetFace-Body Center Y-618',
						'zDetFace-Body Height-619',
						'zDetFace-Body Width-620',
						'zDetFace-Roll-621',
						'zDetFace-Size-622',
						'zDetFace-Cluster Squence Number-623',
						'zDetFace-Blur Score-624',
						'zDetFacePrint-Face Print Version-625',
						'zMedAnlyAstAttr-Face Count-626',
						'zDetFaceGroup-UUID-4TableStart-627',
						'zDetFaceGroup-Person Builder State-628',
						'zDetFaceGroup-UnNamed Face Count-629',
						'zPerson-In Person Naming Model-630',
						'zPerson-Key Face Pick Source Key-631',
						'zPerson-Manual Order Key-632',
						'zPerson-Question Type-633',
						'zPerson-Suggested For Client Type-634',
						'zPerson-Merge Target Person-635',
						'zPerson-Cloud Local State-636',
						'zFaceCrop-Cloud Local State-637',
						'zFaceCrop-Cloud Type-638',
						'zPerson-Cloud Delete State-639',
						'zFaceCrop-Cloud Delete State-640',
						'zFaceCrop-Invalid Merge Canidate Person UUID-4TableStart-641',
						'zAsset-Highlight Visibility Score-642',
						'zMemory-UUID-4TableStart-643',
						'zMemory-AssetListPredicte-644',
						'zMemory-Score-645',
						'zMemory-SubTitle-646',
						'zMemory-Title-647',
						'zMemory-Category-648',
						'zMemory-SubCategory-649',
						('zMemory-Creation Date-650', 'datetime'),
						('zMemory-Last Enrichment Date-651', 'datetime'),
						'zMemory-User Action Options-652',
						'zMemory-Favorite Memory-653',
						'zMemory-View Count-654',
						'zMemory-Play Count-655',
						'zMemory-Rejected-656',
						'zMemory-Share Count-657',
						'zMemory-Sharing Composition-658',
						('zMemory-Last Movie Play Date-659', 'datetime'),
						('zMemory-Last Viewed Date-660', 'datetime'),
						'zMemory-Pending Play Count Memory-661',
						'zMemory-Pending Share Count Memory-662',
						'zMemory-Pending View Count Memory-663',
						'zMemory-Pending State-664',
						'zMemory-Featured State-665',
						'zMemory-Photos Graph Version-666',
						'zMemory-Graph Memory Identifier-667',
						'zMemory-Notification State-668',
						'zMemory-Cloud Local State-669',
						'zMemory-Cloud Delete State-670',
						'zMemory-Story Color Grade Kind-671',
						'zMemory-Story Serialized Title Category-672',
						'zMemory-Syndicated Content State-673',
						'zMemory-Search Index Rebuild State-674',
						'zMemory-Black Listed Feature-675',
						'zMoment-UUID-4TableStart-676',
						'zMoment-Aggregation Score-677',
						('zMoment-Start Date-678', 'datetime'),
						('zMoment-Representative Date-679', 'datetime'),
						'zMoment-Timezone Offset-680',
						('zMoment-Modification Date-681', 'datetime'),
						('zMoment-End Date-682', 'datetime'),
						'zMoment-SubTitle-683',
						'zMoment-Title-684',
						'zMoment-Originator State-685',
						'zMoment-Sharing Composition-686',
						'zMoment-Cached Count Shared-687',
						'zMoment-Processed Location-688',
						'zMoment-Approx Latitude-689',
						'zMoment-Approx Longitude-690',
						'zMoment-GPS Horizontal Accuracy-691',
						'zMoment-Cache Count-692',
						'zMoment-Cached Photos Count-693',
						'zMoment-Cached Videos Count-694',
						'zMoment-Trashed State-695',
						'SBKAzSugg-UUID-4TableStart-696',
						'SBKAzSugg-Suggestion Context-697',
						'SBKAzSugg-Sharing Composition-698',
						('SBKAzSugg-Start Date-699', 'datetime'),
						'SBKAzSugg-State-700',
						'SBKAzSugg-Featured State-701',
						'SBKAzSugg-Notification State-702',
						('SBKAzSugg-Creation Date-703', 'datetime'),
						('SBKAzSugg-End Date-704', 'datetime'),
						('SBKAzSugg-Activation Date-705', 'datetime'),
						('SBKAzSugg-Expunge Date-706', 'datetime'),
						('SBKAzSugg-Relevant Until Date-707', 'datetime'),
						'SBKAzSugg-Title-708',
						'SBKAzSugg-Sub Title-709',
						'SBKAzSugg-Cached Count-710',
						'SBKAzSugg-Cahed Photos Count-711',
						'SBKAzSugg-Cached Videos Count-712',
						'SBKAzSugg-Type-713',
						'SBKAzSugg-Sub Type-714',
						'SBKAzSugg-Action Data-715',
						'SBKAzSugg-Version-716',
						'SBKAzSugg-Cloud Local State-717',
						'SBKAzSugg-Cloud Delete State-718',
						'SBRAzSugg-UUID-4TableStart-719',
						'SBRAzSugg-Suggestion Context-720',
						'SBRAzSugg-Sharing Composition-721',
						('SBRAzSugg-Start Date-722', 'datetime'),
						'SBRAzSugg-State-723',
						'SBRAzSugg-Featured State-724',
						'SBRAzSugg-Notification State-725',
						('SBRAzSugg-Creation Date-726', 'datetime'),
						('SBRAzSugg-End Date-727', 'datetime'),
						('SBRAzSugg-Activation Date-728', 'datetime'),
						('SBRAzSugg-Expunge Date-729', 'datetime'),
						('SBRAzSugg-Relevant Until Date-730', 'datetime'),
						'SBRAzSugg-Title-731',
						'SBRAzSugg-Sub Title-732',
						'SBRAzSugg-Cached Count-733',
						'SBRAzSugg-Cahed Photos Count-734',
						'SBRAzSugg-Cached Videos Count-735',
						'SBRAzSugg-Type-736',
						'SBRAzSugg-Sub Type-737',
						'SBRAzSugg-Action Data-738',
						'SBRAzSugg-Version-739',
						'SBRAzSugg-Cloud Local State-740',
						'SBRAzSugg-Cloud Delete State-741',
						'zMedAnlyAstAttr-Media Analysis Version-742',
						'zMedAnlyAstAttr-Audio Classification-743',
						'zMedAnlyAstAttr-Best Video Range Duration Time Scale-744',
						'zMedAnlyAstAttr-Best Video Range Start Time Scale-745',
						'zMedAnlyAstAttr-Best Video Range Duration Value-746',
						'zMedAnlyAstAttr-Best Video Range Start Value-747',
						'zMedAnlyAstAttr-Packed Best Playback Rect-748',
						'zMedAnlyAstAttr-Activity Score-749',
						'zMedAnlyAstAttr-Video Score-750',
						'zMedAnlyAstAttr-Audio Score-751',
						'zMedAnlyAstAttr-Wallpaper Score-752',
						'zMedAnlyAstAttr-AutoPlay Suggestion Score-753',
						'zMedAnlyAstAttr-Blurriness Score-754',
						'zMedAnlyAstAttr-Exposure Score-755',
						'zMedAnlyAstAttr-Probable Rotation Direction Confidence-756',
						'zMedAnlyAstAttr-Probable Rotation Direction-757',
						'zMedAnlyAstAttr-Screen Time Device Image Sensitivity-758',
						'zAssetAnalyState-Asset UUID-4TableStart-759',
						'zAssetAnalyState-Analyisis State-760',
						'zAssetAnalyState-Worker Flags-761',
						'zAssetAnalyState-Worker Type-762',
						('zAssetAnalyState-Ignore Until Date-763', 'datetime'),
						('zAssetAnalyState-Last Ignored Date-764', 'datetime'),
						('zAssetAnalyState-Sort Token-765', 'datetime'),
						'zMedAnlyAstAttr-Character Recognition Attr-766',
						'zCharRecogAttr-Algorithm Version-767',
						'zCharRecogAttr-Adjustment Version-768',
						'zMedAnlyAstAttr-Visual Search Attributes-769',
						'zVisualSearchAttr-Algorithm Version-770',
						'zVisualSearchAttr-Adjustment Version-771',
						'zAsset-Overall Aesthetic Score-772',
						'zCompAssetAttr-Behavioral Score-773',
						'zCompAssetAttr-Failure Score zCompAssetAttr-774',
						'zCompAssetAttr-Harmonious Color Score-775',
						'zCompAssetAttr-Immersiveness Score-776',
						'zCompAssetAttr-Interaction Score-777',
						'zCompAssetAttr-Intersting Subject Score-778',
						'zCompAssetAttr-Intrusive Object Presence Score-779',
						'zCompAssetAttr-Lively Color Score-780',
						'zCompAssetAttr-Low Light-781',
						'zCompAssetAttr-Noise Score-782',
						'zCompAssetAttr-Pleasant Camera Tilt Score-783',
						'zCompAssetAttr-Pleasant Composition Score-784',
						'zCompAssetAttr-Pleasant Lighting Score-785',
						'zCompAssetAttr-Pleasant Pattern Score-786',
						'zCompAssetAttr-Pleasant Perspective Score-787',
						'zCompAssetAttr-Pleasant Post Processing Score-788',
						'zCompAssetAttr-Pleasant Reflection Score-789',
						'zCompAssetAttrPleasant Symmetry Score-790',
						'zCompAssetAttr-Sharply Focused Subject Score-791',
						'zCompAssetAttr-Tastfully Blurred Score-792',
						'zCompAssetAttr-Well Chosen Subject Score-793',
						'zCompAssetAttr-Well Framed Subject Score-794',
						'zCompAssetAttr-Well Timeed Shot Score-795',
						'zCldRes-Asset UUID-4TableStart-796',
						'zCldRes-Cloud Local State-797',
						'zCldRes-File Size-798',
						'zCldRes-Height-799',
						'zCldRes-Is Available-800',
						'zCldRes-Is Locally Available-801',
						'zCldRes-Prefetch Count-802',
						'zCldRes-Source Type-803',
						'zCldRes-Type-804',
						'zCldRes-Width-805',
						('zCldRes-Date Created-806', 'datetime'),
						('zCldRes-Last OnDemand Download Date-807', 'datetime'),
						('zCldRes-Last Prefetch Date-808', 'datetime'),
						'zCldRes-Prunedat-809',
						'zCldRes-File Path-810',
						'zCldRes-Fingerprint-811',
						'zCldRes-Item ID-812',
						'zCldRes-UniID-813',
						'zUserFeedback-UUID-4TableStart-814',
						'zUserFeedback-Feature-815',
						'zUserFeedback-Type-816',
						('zUserFeedback-Last Modified Date-817', 'datetime'),
						'zUserFeedback-Context-818',
						'zUserFeedback-Cloud Local State-819',
						'zUserFeedback-Cloud Delete State-820',
						'zAddAssetAttr-zPK-821',
						'zAddAssetAttr-zENT-822',
						'ZAddAssetAttr-zOPT-823',
						'zAddAssetAttr-zAsset= zAsset_zPK-824',
						'zAddAssetAttr-UnmanAdjust Key= zUnmAdj.zPK-825',
						'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-826',
						'zAddAssetAttr-Master Fingerprint-827',
						'zAddAssetAttr-Public Global UUID-828',
						'zAddAssetAttr-Deferred Photo Identifier-829',
						'zAddAssetAttr-Original Assets UUID-830',
						'zAddAssetAttr-Import Session ID-831',
						'zAddAssetAttr-Originating Asset Identifier-832',
						'zAddAssetAttr.Adjusted Fingerprint-833',
						'zAlbumList-zPK= Album List Key-834',
						'zAlbumList-zENT-835',
						'zAlbumList-zOPT-836',
						'zAlbumList-ID Key-837',
						'zAlbumList-UUID-838',
						'zAsset-zPK-839',
						'zAsset-zENT-840',
						'zAsset-zOPT-841',
						'zAsset-Master= zCldMast-zPK-842',
						'zAsset-Extended Attributes= zExtAttr-zPK-843',
						'zAsset-Import Session Key-844',
						'zAsset-Trashed by Participant= zSharePartic_zPK-845',
						'zAsset-Photo Analysis Attributes Key-846',
						'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-847',
						'zAsset-FOK-Cloud Feed Asset Entry Key-848',
						'zAsset-Moment Share Key= zShare-zPK-849',
						'zAsset-zMoment Key= zMoment-zPK-850',
						'zAsset-Computed Attributes Asset Key-851',
						'zAsset-Highlight Being Assets-HBA Key-852',
						'zAsset-Highlight Being Extended Assets-HBEA Key-853',
						'zAsset-Highlight Being Key Asset Private-HBKAP Key-854',
						'zAsset-Highlight Being Key Asset Shared-HBKAS Key-855',
						'zAsset-Highligh Being Summary Assets-HBSA Key-856',
						'zAsset-Day Group Highlight Being Assets-DGHBA Key-857',
						'zAsset-Day Group Highlight Being Extended Assets-DGHBEA Key-858',
						'zAsset-Day Group Highlight Being Key Asset Private-DGHBKAP Key-859',
						'zAsset-Day Group Highlight Being Key Asset Shared-DGHBKAS Key-860',
						'zAsset-Day Group Highlight Being Summary Assets-DGHBSA Key-861',
						'zAsset-Month Highlight Being Key Asset Private-MHBKAP Key-862',
						'zAsset-Month Highlight Being Key Asset Shared-MHBKAS Key-863',
						'zAsset-Year Highlight Being Key Asset Private-YHBKAP Key-864',
						'zAsset-Year Highlight Being Key Asset Shared-YHBKAS Key-865',
						'zAsset-Promotion Score-866',
						'zAsset-Media Analysis Attributes Key-867',
						'zAsset-Media Group UUID-868',
						'zAsset-UUID = store.cloudphotodb-869',
						'zAsset-Cloud_Asset_GUID = store.cloudphotodb-870',
						'zAsset.Cloud Collection GUID-871',
						'zAsset-Avalanche UUID-872',
						'zAssetAnalyState-zPK-873',
						'zAssetAnalyState-zEnt-874',
						'zAssetAnalyState-zOpt-875',
						'zAssetAnalyState-Asset= zAsset-zPK-876',
						'zAssetAnalyState-Asset UUID-877',
						'zAsstContrib-zPK-878',
						'zAsstContrib-zEnt-879',
						'zAsstContrib-zOpt-880',
						'zAsstContrib-3Library Scope Asset Contributors= zAssset-zPK-881',
						'zAsstContrib-Participant= zSharePartic-zPK-882',
						'zAssetDes-zPK-883',
						'zAssetDes-zENT-884',
						'zAssetDes-zOPT-885',
						'zAssetDes-Asset Attributes Key= zAddAssetAttr-zPK-886',
						'zCharRecogAttr-zPK-887',
						'zCharRecogAttr-zENT-888',
						'zCharRecogAttr-zOPT-889',
						'zCharRecogAttr-MedAssetAttr= zMedAnlyAstAttr-zPK-890',
						'zCldFeedEnt-zPK= zCldShared keys-891',
						'zCldFeedEnt-zENT-892',
						'zCldFeedEnt-zOPT-893',
						'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-894',
						'zCldFeedEnt-Entry Invitation Record GUID-895',
						'zCldFeedEnt-Entry Cloud Asset GUID-896',
						'zCldMast-zPK= zAsset-Master-897',
						'zCldMast-zENT-898',
						'zCldMast-zOPT-899',
						'zCldMast-Moment Share Key= zShare-zPK-900',
						'zCldMast-Media Metadata Key= zCldMastMedData.zPK-901',
						'zCldMast-Cloud_Master_GUID = store.cloudphotodb-902',
						'zCldMast-Originating Asset ID-903',
						'zCldMast-Import Session ID- AirDrop-StillTesting-904',
						'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-905',
						'CMzCldMastMedData-zENT-906',
						'CMzCldMastMedData-zOPT-907',
						'CMzCldMastMedData-CldMast= zCldMast-zPK-908',
						'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-909',
						'AAAzCldMastMedData-zENT-910',
						'AAAzCldMastMedData-zOPT-911',
						'AAAzCldMastMedData-CldMast key-912',
						'AAAzCldMastMedData-AddAssetAttr= AddAssetAttr-zPK-913',
						'zCldRes-zPK-914',
						'zCldRes-zENT-915',
						'zCldRes-zOPT-916',
						'zCldRes-Asset= zAsset-zPK-917',
						'zCldRes-Cloud Master= zCldMast-zPK-918',
						'zCldRes-Asset UUID-919',
						'zCldShareAlbumInvRec-zPK-920',
						'zCldShareAlbumInvRec-zEnt-921',
						'zCldShareAlbumInvRec-zOpt-922',
						'zCldShareAlbumInvRec-Album Key-923',
						'zCldShareAlbumInvRec-FOK Album Key-924',
						'zCldShareAlbumInvRec-Album GUID-925',
						'zCldShareAlbumInvRec-zUUID-926',
						'zCldShareAlbumInvRec-Cloud GUID-927',
						'zCldSharedComment-zPK-928',
						'zCldSharedComment-zENT-929',
						'zCldSharedComment-zOPT-930',
						'zCldSharedComment-Commented Asset Key= zAsset-zPK-931',
						'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-932',
						'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-933',
						'zCldSharedComment-Liked Asset Key= zAsset-zPK-934',
						'zCldSharedComment-CldFeedLikeCommentEntry Key-935',
						'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-936',
						'zCldSharedComment-Cloud GUID-937',
						'zCompAssetAttr-zPK-938',
						'zCompAssetAttr-zEnt-939',
						'zCompAssetAttr-zOpt-940',
						'zCompAssetAttr-Asset Key-941',
						'zDetFace-zPK-942',
						'zDetFace-zEnt-943',
						'zDetFace.zOpt-944',
						'zDetFace-Asset= zAsset-zPK or Asset Containing Face-945',
						'zDetFace-Person= zPerson-zPK-946',
						'zDetFace-Person Being Key Face-947',
						'zDetFace-Face Print-948',
						'zDetFace-FaceGroupBeingKeyFace= zDetFaceGroup-zPK-949',
						'zDetFace-FaceGroup= zDetFaceGroup-zPK-950',
						'zDetFace-UUID-951',
						'zDetFaceGroup-zPK-952',
						'zDetFaceGroup-zENT-953',
						'zDetFaceGroup-zOPT-954',
						'zDetFaceGroup-AssocPerson= zPerson-zPK-955',
						'zDetFaceGroup-KeyFace= zDetFace-zPK-956',
						'zDetFaceGroup-UUID-957',
						'zDetFacePrint-zPK-958',
						'zDetFacePrint-zEnt-959',
						'zDetFacePrint-zOpt-960',
						'zDetFacePrint-Face Key-961',
						'zExtAttr-zPK= zAsset-zExtendedAttributes-962',
						'zExtAttr-zENT-963',
						'zExtAttr-zOPT-964',
						'zExtAttr-Asset Key-965',
						'zFaceCrop-zPK-966',
						'zFaceCrop-zEnt-967',
						'zFaceCrop-zOpt-968',
						'zFaceCrop-Asset Key-969',
						'zFaceCrop-Invalid Merge Canidate Person UUID-970',
						'zFaceCrop-Person=zPerson-zPK&zDetFace-Person-Key-971',
						'zFaceCrop-Face Key-972',
						'zFaceCrop-UUID-973',
						'zGenAlbum-zPK=26AlbumLists= 26Albums-974',
						'zGenAlbum-zENT-975',
						'zGenAlbum-zOpt-976',
						'zGenAlbum-Key Asset-Key zAsset-zPK-977',
						'zGenAlbum-Secondary Key Asset-978',
						'zGenAlbum-Tertiary Key Asset-979',
						'zGenAlbum-Custom Key Asset-980',
						'zGenAlbum-Parent Folder Key= zGenAlbum-zPK-981',
						'zGenAlbum-FOK Parent Folder-982',
						'zGenAlbum-zSyndicate-983',
						'zGenAlbum-UUID-984',
						'SWYConverszGenAlbum-UUID-985',
						'zGenAlbum-Cloud_GUID = store.cloudphotodb-986',
						'SWYConverszGenAlbum-Cloud GUID-987',
						'zGenAlbum-Project Render UUID-988',
						'SWYConverszGenAlbum-Project Render UUID-989',
						'zIntResou-zPK-990',
						'zIntResou-zENT-991',
						'zIntResou-zOPT-992',
						'zIntResou-Asset= zAsset_zPK-993',
						'zIntResou-Fingerprint-994',
						'zIntResou-Cloud Delete Asset UUID With Resource Type-995',
						'zMedAnlyAstAttr-zPK= zAddAssetAttr-Media Metadata-996',
						'zMedAnlyAstAttr-zEnt-997',
						'zMedAnlyAstAttr-zOpt-998',
						'zMedAnlyAstAttr-Asset= zAsset-zPK-999',
						'zMemory-zPK-1000',
						'zMemory-zENT-1001',
						'zMemory-zOPT-1002',
						'zMemory-Key Asset= zAsset-zPK-1003',
						'zMemory-UUID-1004',
						'zMoment-zPK-1005',
						'zMoment-zENT-1006',
						'zMoment-zOPT-1007',
						'zMoment-Highlight Key-1008',
						'zMoment-UUID-1009',
						'zPerson-zPK=zDetFace-Person-1010',
						'zPerson-zEnt-1011',
						'zPerson-zOpt-1012',
						'zPerson-Share Participant= zSharePartic-zPK-1013',
						'zPerson-KeyFace=zDetFace-zPK-1014',
						'zPerson-Assoc Face Group Key-1015',
						'zPerson-Person UUID-1016',
						'zPhotoAnalysisAssetAttr-zPK-1017',
						'zPhotoAnalysisAssetAttr-zEnt-1018',
						'zPhotoAnalysisAssetAttr-zOpt-1019',
						'zPhotoAnalysisAssetAttr-zAsset = zAsset-zPK-1020',
						'zSceneP-zPK-1021',
						'zSceneP-zENT-1022',
						'zSceneP-zOPT-1023',
						'zShare-zPK-1024',
						'zShare-zENT-1025',
						'zShare-zOPT-1026',
						'zShare-UUID-1027',
						'SPLzShare-UUID-1028',
						'zShare-Scope ID = store.cloudphotodb-1029',
						'zSharePartic-zPK-1030',
						'zSharePartic-zENT-1031',
						'zSharePartic-zOPT-1032',
						'zSharePartic-Share Key= zShare-zPK-1033',
						'zSharePartic-Person= zPerson-zPK-1034',
						'zSharePartic-UUID-1035',
						'SBKAzSugg-zPK-1036',
						'SBKAzSugg-zENT-1037',
						'SBKAzSugg-zOPT-1038',
						'SBKAzSugg-UUID-1039',
						'SBRAzSugg-zPK-1040',
						'SBRAzSugg-zENT-1041',
						'SBRAzSugg-zOPT-1042',
						'SBRAzSugg-UUID-1043',
						'z3SuggBRA-3RepAssets1-1044',
						'z3SuggBRA-58SuggBeingRepAssets-1045',
						'z3SuggBKA-58SuggBeingKeyAssets= zSugg-zPK-1046',
						'z3SuggBKA-3KeyAssets= zAsset-zPK-1047',
						'zUnmAdj-zPK=zAddAssetAttr.ZUnmanAdj Key-1048',
						'zUnmAdj-zOPT-1049',
						'zUnmAdj-zENT-1050',
						'zUnmAdj-Asset Attributes= zAddAssetAttr.zPK-1051',
						'zUnmAdj-UUID-1052',
						'zUnmAdj-Other Adjustments Fingerprint-1053',
						'zUnmAdj-Similar to Orig Adjustments Fingerprint-1054',
						'zUserFeedback-zPK-1055',
						'zUserFeedback-zENT-1056',
						'zUserFeedback-zOPT-1057',
						'zUserFeedback-Person= zPerson-zPK-1058',
						'zUserFeedback-Memory= zMemory-zPK-1059',
						'zUserFeedback-UUID-1060',
						'zVisualSearchAttr-zPK-1061',
						'zVisualSearchAttr-zENT-1062',
						'zVisualSearchAttr-zOPT-1063',
						'zVisualSearchAttr-MedAssetAttr= zMedAnlyAstAttr-zPK-1064',
						'z27AlbumList-27Albums= zGenAlbum-zPK-1065',
						'z27AlbumList-Album List Key-1066',
						'z27AlbumList-FOK27Albums Key-1067',
						'z28Assets-28Albums= zGenAlbum-zPK-1068',
						'z28Assets-3Asset Key= zAsset-zPK in the Album-1069',
						'z28Asset-FOK-3Assets= zAsset.Z_FOK_CLOUDFEEDASSETSENTRY-1070',
						'z3MemoryBMCAs-3MovieCuratedAssets= zAsset-zPK-1071',
						'z3MemoryBCAs-3CuratedAssets= zAsset-zPK-1072',
						'z3MemoryBCAs-44MemoriesBeingCuratedAssets= zMemory-zPK-1073',
						'z3MemoryBECAs-3ExtCuratedAssets= zAsset-zPK-1074',
						'z3MemoryBECAs-44MemoriesBeingExtCuratedAssets= zMemory-zPK-1075',
						'z3MemoryBRAs-3RepresentativeAssets= zAsset-zPK-1076',
						'z3MemoryBRAs-44RepresentativeAssets= zMemory-zPK-1077',
						'z3MemoryBUCAs-3UserCuratedAssets= zAsset-zPK-1078',
						'z3MemoryBUCAs-44MemoriesBeingUserCuratedAssets= zMemory-zPK-1079',
						'z3MemoryBCAs-44Memories Being Custom User Assets-1080',
						'z3MemoryBCAs-3Custom User Assets-1081',
						'z3MemoryBCAs-FOK-3Custom User Assets-1082')
		data_list = get_sqlite_db_records(source_path, query)

		return data_headers, data_list, source_path
