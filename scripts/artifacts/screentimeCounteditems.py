import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_screentimeCounteditems(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("12"):
		logfunc("Unsupported version for Screentime App by Hour on iOS " + iOSversion)
		return ()
	
	
	if version.parse(iOSversion) >= version.parse("13"):
		cursor = db.cursor()
		cursor.execute('''
		SELECT 
				DATETIME(ZUSAGEBLOCK.ZSTARTDATE+978307200,'UNIXEPOCH') AS 'HOUR',
				ZUSAGECOUNTEDITEM.ZBUNDLEIDENTIFIER AS 'BUNDLE ID', 
				ZUSAGECOUNTEDITEM.ZNUMBEROFNOTIFICATIONS AS 'NUMBER OF NOTIFICATIONS',
				ZUSAGECOUNTEDITEM.ZNUMBEROFPICKUPS AS 'NUMBER OF PICKUPS',
				DATETIME(ZUSAGEBLOCK.ZFIRSTPICKUPDATE+978307200,'UNIXEPOCH') AS 'FIRST PICKUP',
				ZUSAGEBLOCK.ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE AS 'NUMBER OF PICKUPS W/O APP USAGE',
				ZCOREDEVICE.ZNAME AS 'NAME',
				ZCOREDEVICE.ZIDENTIFIER AS 'DEVICE ID',
				ZCOREDEVICE.ZLOCALUSERDEVICESTATE AS 'LOCAL USER DEVICE STATE',
				CASE ZCOREDEVICE.ZPLATFORM
					WHEN 0 THEN 'Unknown'
					WHEN 1 THEN 'macOS'
					WHEN 2 THEN 'iOS'
					WHEN 4 THEN 'Apple Watch'
					ELSE ZPLATFORM
				END AS PLATFORM,
				ZCOREUSER.ZGIVENNAME AS 'GIVEN NAME',
				ZCOREUSER.ZFAMILYNAME AS 'FAMILY NAME',
				ZCOREUSER.ZFAMILYMEMBERTYPE AS 'FAMILY MEMBER TYPE',
				ZCOREUSER.ZAPPLEID AS 'APPLE ID',
				ZCOREUSER.ZDSID AS 'DSID',
				ZCOREUSER.ZALTDSID AS 'ALT DSID',
				ZUSAGECOUNTEDITEM.Z_PK AS "ZUSAGECOUNTEDITEM TABLE ID"
			FROM ZUSAGECOUNTEDITEM
			LEFT JOIN ZUSAGEBLOCK ON ZUSAGECOUNTEDITEM.ZBLOCK == ZUSAGEBLOCK.Z_PK
			LEFT JOIN ZUSAGE ON ZUSAGEBLOCK.ZUSAGE == ZUSAGE.Z_PK
			LEFT JOIN ZCOREUSER ON ZUSAGE.ZUSER == ZCOREUSER.Z_PK
			LEFT JOIN ZCOREDEVICE ON ZUSAGE.ZDEVICE == ZCOREDEVICE.Z_PK
			''')
	else:
			cursor = db.cursor()
			cursor.execute('''
			SELECT 
					DATETIME(ZUSAGEBLOCK.ZSTARTDATE+978307200,'UNIXEPOCH') AS 'HOUR',
					ZUSAGECOUNTEDITEM.ZBUNDLEIDENTIFIER AS 'BUNDLE ID', 
					ZUSAGECOUNTEDITEM.ZNUMBEROFNOTIFICATIONS AS 'NUMBER OF NOTIFICATIONS',
					ZUSAGECOUNTEDITEM.ZNUMBEROFPICKUPS AS 'NUMBER OF PICKUPS',
					DATETIME(ZUSAGEBLOCK.ZFIRSTPICKUPDATE+978307200,'UNIXEPOCH') AS 'FIRST PICKUP',
					ZUSAGEBLOCK.ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE AS 'NUMBER OF PICKUPS W/O APP USAGE',
					ZCOREDEVICE.ZNAME AS 'NAME',
					ZCOREDEVICE.ZIDENTIFIER AS 'DEVICE ID',
					ZCOREDEVICE.ZLOCALUSERDEVICESTATE AS 'LOCAL USER DEVICE STATE',
					ZCOREUSER.ZGIVENNAME AS 'GIVEN NAME',
					ZCOREUSER.ZFAMILYNAME AS 'FAMILY NAME',
					ZCOREUSER.ZFAMILYMEMBERTYPE AS 'FAMILY MEMBER TYPE',
					ZCOREUSER.ZAPPLEID AS 'APPLE ID',
					ZCOREUSER.ZDSID AS 'DSID',
					ZUSAGECOUNTEDITEM.Z_PK AS "ZUSAGECOUNTEDITEM TABLE ID"
				FROM ZUSAGECOUNTEDITEM
				LEFT JOIN ZUSAGEBLOCK ON ZUSAGECOUNTEDITEM.ZBLOCK == ZUSAGEBLOCK.Z_PK
				LEFT JOIN ZUSAGE ON ZUSAGEBLOCK.ZUSAGE == ZUSAGE.Z_PK
				LEFT JOIN ZCOREUSER ON ZUSAGE.ZUSER == ZCOREUSER.Z_PK
				LEFT JOIN ZCOREDEVICE ON ZUSAGE.ZDEVICE == ZCOREDEVICE.Z_PK
			''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("13"):
					
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

			report = ArtifactHtmlReport('Screentime Counted Items')
			report.start_artifact_report(report_folder, 'Counted Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Number of Notifications','Number of Pickups', 'First Pickup','Number of Pickups W/O App Usage','Name','Device ID','Local User Device State','Platform','Given Name','Family Name','Family Member Type','AppleID','DSID','Alt DSID','Table ID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Generic by Hour'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			for row in all_rows: 
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
					
			report = ArtifactHtmlReport('Screentime Counted Items')
			report.start_artifact_report(report_folder, 'Counted Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Number of Notifications','Number of Pickups', 'First Pickup','Number of Pickups W/O App Usage','Name','Device ID','Local User Device State','Given Name','Family Name','Family Member Type','AppleID','DSID','Table ID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Timed Items'
			tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table foe Screentime Counted Items')

	db.close()
	return      
