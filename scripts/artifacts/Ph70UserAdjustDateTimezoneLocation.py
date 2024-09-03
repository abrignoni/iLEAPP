# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 2.0
#
#   Description:
#   Parses iOS 15-18 asset records from PhotoData-Photos.sqlite for assets that might have
#   a user adjusted Date & TimeZone & Location. This parser should provide data for investigative analysis
#   of assets where a user might have adjusted the Date AND the Timezone AND the Location of an asset from
#   within the Apple Photos Application (com.apple.mobileslideshow) I recommend opening the TSV generated
#   report with Zimmerman's Tools https://ericzimmerman.github.io/#!index.md
#   TimelineExplorer to view, search and filter the results.
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph70adjusteddatetimezonelocphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Date & Timezone & Location for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':'))) & (zAddAssetAttr.ZTIMEZONEOFFSET <> 
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET) & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date & TimeZone & Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)' \
				' & (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)' \
				' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)'
			report = ArtifactHtmlReport('Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date & Timezone & Location data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK		
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':'))) & (zAddAssetAttr.ZTIMEZONEOFFSET <> 
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET) & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date & TimeZone & Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)' \
				' & (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)' \
				' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph70.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date & Timezone & Location data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


def get_ph71adjusteddatetimezonephdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Date & Timezone for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':'))) & (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date & TimeZone' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)' \
				' & (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)',
			report = ArtifactHtmlReport('Ph71.1-Possible_Adjust_Date-Timezone-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph71.1-Possible_Adjust_Date-Timezone-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph71.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph71.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date & Timezone data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK		
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':'))) & (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date & TimeZone' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)' \
				' & (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)',
			report = ArtifactHtmlReport('Ph71.1-Possible_Adjust_Date-Timezone-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph71.1-Possible_Adjust_Date-Timezone-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph71.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph71.1-Possible_Adjust_Date-Timezone-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date & Timezone data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


def get_ph72adjusteddatelocphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Date & Location for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':'))) & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date & Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)' \
				' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph72.1-Possible_Adjust_Date-Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph72.1-Possible_Adjust_Date-Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph72.1-Possible_Adjust_Date-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph72.1-Possible_Adjust_Date-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date & Location data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':'))) & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date & Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)' \
				' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph72.1-Possible_Adjust_Date-Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph72.1-Possible_Adjust_Date-Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph72.1-Possible_Adjust_Date-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph72.1-Possible_Adjust_Date-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date & Location data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


def get_ph73adjusteddatephdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Date for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':')))
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)',
			report = ArtifactHtmlReport('Ph73.1-Possible_Adjust_Date-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph73.1-Possible_Adjust_Date-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph73.1-Possible_Adjust_Date-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph73.1-Possible_Adjust_Date-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> (REPLACE(strftime('%Y-%m-%d %H:%M:%S', datetime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME')), '-', ':')))
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Date' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)',
			report = ArtifactHtmlReport('Ph73.1-Possible_Adjust_Date-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph73.1-Possible_Adjust_Date-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph73.1-Possible_Adjust_Date-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph73.1-Possible_Adjust_Date-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Date data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


def get_ph74adjustedtimezonelocphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Timezone & Location for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET) & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted TimeZone & Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)' \
				' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Timezone & Location data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET) & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted TimeZone & Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)' \
				' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph74.1-Possible_Adjust_Timezone-Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Timezone & Location data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


def get_ph75adjustedtimezonephdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Timezone for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted TimeZone' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)',
			report = ArtifactHtmlReport('Ph75.1-Possible_Adjust_Timezone-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph75.1-Possible_Adjust_Timezone-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph75.1-Possible_Adjust_Timezone-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph75.1-Possible_Adjust_Timezone-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Timezone data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted TimeZone' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)',
			report = ArtifactHtmlReport('Ph75.1-Possible_Adjust_Timezone-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph75.1-Possible_Adjust_Timezone-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph75.1-Possible_Adjust_Timezone-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph75.1-Possible_Adjust_Timezone-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Timezone data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


def get_ph76adjustedlocphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

	for file_found in files_found:
		file_found = str(file_found)

		if file_found.endswith('.sqlite'):
			break

	if report_folder.endswith('/') or report_folder.endswith('\\'):
		report_folder = report_folder[:-1]
	iosversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iosversion) <= version.parse("14.8.1"):
		logfunc("Unsupported version for PhotoData-Photos.sqlite User Adjusted Location for iOS " + iosversion)
	if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
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
		CASE zAsset.ZHASADJUSTMENTS
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 1 THEN '1-Yes-Adjustments-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
		END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modificaion Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph76.1-Possible_Adjust_Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph76.1-Possible_Adjust_Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Saved Asset Type-54',
							'zAsset-Kind-55',
							'zAsset-Kind-Sub-Type-56',
							'zAddAssetAttr-Cloud Kind Sub Type-57',
							'zAsset-Playback Style-58',
							'zAsset-Playback Variation-59',
							'zAsset-Has Adjustments-Camera-Effects-Filters-60',
							'zAsset-Adjustment Timestamp-61',
							'zAddAssetAttr-Editor Bundle ID-62',
							'zMedAnlyAstAttr-Media Analysis Timestamp-63',
							'zAsset-Analysis State Modification Date-64',
							'zAddAssetAttr-Scene Analysis Timestamp-65',
							'zAsset-zPK-66',
							'zAddAssetAttr-zPK-67',
							'zAsset-UUID = store.cloudphotodb-68',
							'zAddAssetAttr-Master Fingerprint-69')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph76.1-Possible_Adjust_Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph76.1-Possible_Adjust_Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Location data detected in iOS15-17 PhotoData-Photos.sqlite')

		db.close()
		return

	elif version.parse(iosversion) >= version.parse("18"):
		file_found = str(files_found[0])
		db = open_sqlite_db_readonly(file_found)
		cursor = db.cursor()

		cursor.execute("""
		SELECT
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created-UTC',
		DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH', 'LOCALTIME') AS 'zAsset-Date Created-Local',
		DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
		DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
		DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
		zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
		zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
		zAddAssetAttr.ZINFERREDTIMEZONEOFFSET AS 'zAddAssetAttr-Inferred Time Zone Offset',
		zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',		
		CASE zAddAssetAttr.ZDATECREATEDSOURCE
			WHEN 0 THEN '0-Cloud-Asset-0'
			WHEN 1 THEN '1-Local_Asset_EXIF-1'
			WHEN 3 THEN '3-Local_Asset_No_EXIF-3'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZDATECREATEDSOURCE || ''
		END AS 'zAddAssetAttr-Date Created Source',		
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
		zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
		zAsset.ZFILENAME AS 'zAsset-Filename',
		zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
		zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
		zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',		
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
			ELSE 'zAddAssetAttr-Shifted_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Shifted Location Data-Indicator',
		zAddAssetAttr.ZSHIFTEDLOCATIONDATA AS 'zAddAssetAttr-Shifted Location Data',		
		CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
			WHEN 0 THEN '0-Reverse Location Not Valid-0'
			WHEN 1 THEN '1-Reverse Location Valid-1'
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
		END AS 'zAddAssetAttr-Reverse Location Is Valid',		
		CASE
			WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
			ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
		END AS 'zAddAssetAttr-Reverse Location Data-Indicator',		
		zAddAssetAttr.ZREVERSELOCATIONDATA AS 'zAddAssetAttr-Reverse Location Data',		
		zAddAssetAttr.ZMEDIAMETADATA AS 'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK',
		AAAzCldMastMedData.Z_PK AS 'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData',
		CASE
			WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
			ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
		END AS 'AAAzCldMastMedData-Data-HasDataIndicator',
		AAAzCldMastMedData.ZDATA AS 'AAAzCldMastMedData-Data',
		CASE CMzCldMastMedData.Z_OPT
			WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
			WHEN 2 THEN '2-StillTesting-Local_Asset-2'
			WHEN 3 THEN '3-StillTesting-Muted-3'
			WHEN 4 THEN '4-StillTesting-Unknown-4'
			WHEN 5 THEN '5-StillTesting-Unknown-5'
			ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
		END AS 'CldMasterzCldMastMedData-zOPT',
		zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',
		zCldMast.ZMEDIAMETADATA AS 'zCldMast-Media Metadata Key= zCldMastMedData.zPK',
		CMzCldMastMedData.Z_PK AS 'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key',
		CASE
			WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
			ELSE 'CMzCldMastMedData-Data_Empty-NULL'
		END AS 'CMzCldMastMedData-Data-HasDataIndicator',		
		CMzCldMastMedData.ZDATA AS 'CMzCldMastMedData-Data',		
		zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
		zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
		zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',		
		zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
		zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
		zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
		zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
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
		CASE zAsset.ZKIND
			WHEN 0 THEN '0-Photo-0'
			WHEN 1 THEN '1-Video-1'
		END AS 'zAsset-Kind',
		CASE zAsset.ZKINDSUBTYPE
			WHEN 0 THEN '0-Still-Photo-0'
			WHEN 1 THEN '1-Panorama-1'
			WHEN 2 THEN '2-Live-Photo-2'
			WHEN 10 THEN '10-SpringBoard-Screenshot-10'
			WHEN 100 THEN '100-Video-100'
			WHEN 101 THEN '101-Slow-Mo-Video-101'
			WHEN 102 THEN '102-Time-lapse-Video-102'
			WHEN 103 THEN '103-Replay_Screen_Recording-103'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZKINDSUBTYPE || ''
		END AS 'zAsset-Kind-Sub-Type',
		CASE zExtAttr.ZGENERATIVEAITYPE 
			WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type-iOS18',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18',
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
		CASE zAddAssetAttr.ZVIEWPRESENTATION
			WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
			WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
			ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
		END AS 'zAddAssetAttr-View_Presentation-iOS18',
		CASE zAsset.ZADJUSTMENTSSTATE
			WHEN 0 THEN '0-No-Adjustments-0'
			WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
			WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
		END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
		DateTime(zAsset.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAsset-Adjustment Timestamp',
		zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',		
		DateTime(zMedAnlyAstAttr.ZMEDIAANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zMedAnlyAstAttr-Media Analysis Timestamp',
		DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Analysis State Modification Date',		
		DateTime(zAddAssetAttr.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Scene Analysis Timestamp',
		zAsset.Z_PK AS 'zAsset-zPK',
		zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
		zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
		zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18'
		FROM ZASSET zAsset
			LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
			LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
			LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
			LEFT JOIN ZMEDIAANALYSISASSETATTRIBUTES zMedAnlyAstAttr ON zAsset.ZMEDIAANALYSISATTRIBUTES = zMedAnlyAstAttr.Z_PK
		WHERE (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)
		ORDER BY zAsset.ZDATECREATED
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []
		counter = 0
		if usageentries > 0:
			for row in all_rows:
				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				aaashiftedlocation_postal_address = ''
				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				aaareverselocation_postal_address = ''
				# AAAzCldMastMedData.ZDATA-PLIST
				aaazcldmastmeddata_plist_tiff = ''
				aaazcldmastmeddata_plist_exif = ''
				aaazcldmastmeddata_plist_gps = ''
				aaazcldmastmeddata_plist_iptc = ''
				# CMzCldMastMedData.ZDATA-PLIST
				cmzcldmastmeddata_plist_tiff = ''
				cmzcldmastmeddata_plist_exif = ''
				cmzcldmastmeddata_plist_gps = ''
				cmzcldmastmeddata_plist_iptc = ''

				# zAddAssetAttr.ZSHIFTEDLOCATIONDATA-PLIST
				if row[33] is not None:
					pathto = os.path.join(report_folder, 'AAA_ShiftedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[33])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaashiftedlocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# zAddAssetAttr.ZREVERSELOCATIONDATA-PLIST
				if row[36] is not None:
					pathto = os.path.join(report_folder, 'AAA_ReversedLocationData_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[36])

					with open(pathto, 'rb') as f:
						try:
							deserialized_plist = nd.deserialize_plist(f)
							aaareverselocation_postal_address = deserialized_plist

						except (KeyError, ValueError, TypeError) as ex:
							if str(ex).find("does not contain an '$archiver' key") >= 0:
								logfunc('plist was Not an NSKeyedArchive ' + row[21])
							else:
								logfunc('Error reading exported plist from zAsset-Filename' + row[21])

				# AAAzCldMastMedData.ZDATA-PLIST
				if row[40] is not None:
					pathto = os.path.join(report_folder, 'AAAzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[40])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								aaazcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								aaazcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								aaazcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								aaazcldmastmeddata_plist_iptc = val

				# CMzCldMastMedData.ZDATA-PLIST
				if row[46] is not None:
					pathto = os.path.join(report_folder, 'CMzCldMastMedData-Data_' + row[21] + '.plist')
					with open(pathto, 'ab') as wf:
						wf.write(row[46])

					with open(pathto, "rb") as fp:
						plist = plistlib.load(fp)

						for key, val in plist.items():
							if key == '{TIFF}':
								cmzcldmastmeddata_plist_tiff = val
							elif key == '{Exif}':
								cmzcldmastmeddata_plist_exif = val
							elif key == '{GPS}':
								cmzcldmastmeddata_plist_gps = val
							elif key == '{IPTC}':
								cmzcldmastmeddata_plist_iptc = val

				data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
								row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
								row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
								row[28], row[29], row[30], row[31], row[32],
								aaashiftedlocation_postal_address,
								row[34], row[35],
								aaareverselocation_postal_address,
								row[37], row[38], row[39],
								aaazcldmastmeddata_plist_tiff,
								aaazcldmastmeddata_plist_exif,
								aaazcldmastmeddata_plist_gps,
								aaazcldmastmeddata_plist_iptc,
								row[41], row[42], row[43], row[44], row[45],
								cmzcldmastmeddata_plist_tiff,
								cmzcldmastmeddata_plist_exif,
								cmzcldmastmeddata_plist_gps,
								cmzcldmastmeddata_plist_iptc,
								row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
								row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
								row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
								row[73]))

				counter += 1

			description = 'Parses asset records from PhotoData-Photos.sqlite. ' \
				' This parser should provide data for investigative' \
				' analysis of assets that might have User Adjusted Location' \
				' data via Photos Application (com.apple.mobileslideshow).' \
				' I recommend opening the TSV generated report with Zimmermans Tools' \
				' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,' \
				' and filter the results.' \
				' WHERE (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
			report = ArtifactHtmlReport('Ph76.1-Possible_Adjust_Location-PhDaPsql')
			report.start_artifact_report(report_folder, 'Ph76.1-Possible_Adjust_Location-PhDaPsql', description)
			report.add_script()
			data_headers = ('zAsset-Date Created-UTC-0',
							'zAsset-Date Created-Local-1',
							'zCldMast-Creation Date-2',
							'zAsset-Added Date-3',
							'zAsset- SortToken -CameraRoll-4',
							'zAddAssetAttr-Time Zone Name-5',
							'zAddAssetAttr-Time Zone Offset-6',
							'zAddAssetAttr-Inferred Time Zone Offset-7',
							'zAddAssetAttr-EXIF-String-8',
							'zAddAssetAttr-Date Created Source-9',
							'zAsset-Modification Date-10',
							'zAsset-Last Shared Date-11',
							'zCldMast-Cloud Local State-12',
							'zCldMast-Import Date-13',
							'zAddAssetAttr-Last Upload Attempt Date-SWY_Files-14',
							'zAddAssetAttr-Import Session ID-15',
							'zAddAssetAttr-Alt Import Image Date-16',
							'zCldMast-Import Session ID- AirDrop-StillTesting-17',
							'zAsset-Cloud Batch Publish Date-18',
							'zAsset-Cloud Server Publish Date-19',
							'zAsset-Directory-Path-20',
							'zAsset-Filename-21',
							'zAddAssetAttr- Original Filename-22',
							'zCldMast- Original Filename-23',
							'zAddAssetAttr- Syndication Identifier-SWY-Files-24',
							'zAsset-Latitude-25',
							'zExtAttr-Latitude-26',
							'zAsset-Longitude-27',
							'zExtAttr-Longitude-28',
							'zAddAssetAttr-GPS Horizontal Accuracy-29',
							'zAddAssetAttr-Location Hash-30',
							'zAddAssetAttr-Shifted Location Valid-31',
							'zAddAssetAttr-Shifted Location Data-Indicator-32',
							'zAddAssetAttr-Shifted Location Data-33',
							'zAddAssetAttr-Reverse Location Is Valid-34',
							'zAddAssetAttr-Reverse Location Data-Indicator-35',
							'zAddAssetAttr-Reverse Location Data-36',
							'zAddAssetAttr-MediaMetadata= AAAzCldMastMedData-zPK-37',
							'AAAzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData-38',
							'AAAzCldMastMedData-Data-HasDataIndicator-39',
							'aaazcldmastmeddata_plist_tiff-40',
							'aaazcldmastmeddata_plist_exif-40',
							'aaazcldmastmeddata_plist_gps-40',
							'aaazcldmastmeddata_plist_iptc-40',
							'CldMasterzCldMastMedData-zOPT-41',
							'zCldMast-Media Metadata Type-42',
							'zCldMast-Media Metadata Key= zCldMastMedData.zPK-43',
							'CMzCldMastMedData-zPK= zAddAssetAttr&zCldMast-MediaMetaData Key-44',
							'CMzCldMastMedData-Data-HasDataIndicator-45',
							'cmzcldmastmeddata_plist_tiff-46',
							'cmzcldmastmeddata_plist_exif-46',
							'cmzcldmastmeddata_plist_gps-46',
							'cmzcldmastmeddata_plist_iptc-46',
							'zExtAttr-Camera Make-47',
							'zExtAttr-Camera Model-48',
							'zExtAttr-Lens Model-49',
							'zAddAssetAttr.Imported by Bundle Identifier-50',
							'zAddAssetAttr-Imported By Display Name-51',
							'zCldMast-Imported by Bundle ID-52',
							'zCldMast-Imported by Display Name-53',
							'zAsset-Is_Recently_Saved-iOS18-54',
							'zAsset-Saved Asset Type-55',
							'zAsset-Kind-56',
							'zAsset-Kind-Sub-Type-57',
							'zExtAttr-Generative_AI_Type-iOS18-58',
							'zExtAttr-Credit-iOS18-59',
							'zAddAssetAttr-Cloud Kind Sub Type-60',
							'zAsset-Playback Style-61',
							'zAsset-Playback Variation-62',
							'zAddAssetAttr-View_Presentation-iOS18-63',
							'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-64',
							'zAsset-Adjustment Timestamp-65',
							'zAddAssetAttr-Editor Bundle ID-66',
							'zMedAnlyAstAttr-Media Analysis Timestamp-67',
							'zAsset-Analysis State Modification Date-68',
							'zAddAssetAttr-Scene Analysis Timestamp-69',
							'zAsset-zPK-70',
							'zAddAssetAttr-zPK-71',
							'zAsset-UUID = store.cloudphotodb-72',
							'zAddAssetAttr-Original Stable Hash-iOS18-73')
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()

			tsvname = 'Ph76.1-Possible_Adjust_Location-PhDaPsql'
			tsv(report_folder, data_headers, data_list, tsvname)

			tlactivity = 'Ph76.1-Possible_Adjust_Location-PhDaPsql'
			timeline(report_folder, tlactivity, data_list, data_headers)

		else:
			logfunc('No User Adjusted Location data detected in iOS18 PhotoData-Photos.sqlite')

		db.close()
		return


__artifacts_v2__ = {
	'Ph70-1-Possible_Adjust_Date-Timezone-Location-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph70.1 Possible Date Timezone Location Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted Date & TimeZone & Location'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime) &'
		' (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET) &'
		' (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph70adjusteddatetimezonelocphdapsql'
	},
	'Ph71-1-Possible_Adjust_Date-Timezone-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph71.1 Possible Date Timezone Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted Date & TimeZone'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime) &'
		' (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph71adjusteddatetimezonephdapsql'
	},
	'Ph72-1-Possible_Adjust_Date-Location-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph72.1 Possible Date Location Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted Date & Location'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime) &'
		' (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph72adjusteddatelocphdapsql'
	},
	'Ph73-1-Possible_Adjust_Date-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph73.1 Possible Date Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted Date'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAddAssetAttr.ZEXIFTIMESTAMPSTRING <> zAsset.ZDATECREATED LocalTime)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph73adjusteddatephdapsql'
	},
	'Ph74-1-Possible_Adjust_Timezone-Location-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph74.1 Possible Timezone Location Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted TimeZone & Location'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)'
		' & (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph74adjustedtimezonelocphdapsql'
	},
	'Ph75-1-Possible_Adjust_Timezone-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph75.1 Possible Timezone Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted TimeZone'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAddAssetAttr.ZTIMEZONEOFFSET <> zAddAssetAttr.ZINFERREDTIMEZONEOFFSET)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph75adjustedtimezonephdapsql'
	},
	'Ph76-1-Possible_Adjust_Location-PhDaPsql': {
		'name': 'PhDaPL Photos.sqlite Ph76.1 Possible Location Adjust',
		'description': 'Parses asset records from PhotoData-Photos.sqlite.'
		' This parser should provide data for investigative'
		' analysis of assets that might have User Adjusted Location'
		' data via Photos Application (com.apple.mobileslideshow).'
		' I recommend opening the TSV generated report with Zimmermans Tools'
		' https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search,'
		' and filter the results. WHERE (zAsset.ZLATITUDE <> zExtAttr.ZLATITUDE)',
		'author': 'Scott Koenig https://theforensicscooter.com/',
		'version': '2.0',
		'date': '2024-06-14',
		'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
		'category': 'Photos.sqlite-H-Possible_User_Adjusted_Data',
		'notes': '',
		'paths': '*/PhotoData/Photos.sqlite*',
		'function': 'get_ph76adjustedlocphdapsql'
	}
}
