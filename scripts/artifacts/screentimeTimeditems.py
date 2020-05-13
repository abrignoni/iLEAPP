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

def get_screentimeTimeditems(files_found, report_folder, seeker):
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
			ZUSAGETIMEDITEM.ZBUNDLEIDENTIFIER AS  'BUNDLE ID',
			ZUSAGETIMEDITEM.ZDOMAIN AS 'DOMAIN',
			CASE ZUSAGECATEGORY.ZIDENTIFIER 
				WHEN 'DH0011' THEN 'Unspecified1'
				WHEN 'DH0012' THEN 'Unspecified2'
				WHEN 'DH0013' THEN 'Unspecified3'
				WHEN 'DH1001' THEN 'Games'
				WHEN 'DH1002' THEN 'Social Networking'
				WHEN 'DH1003' THEN 'Entertainment'
				WHEN 'DH1004' THEN 'Creativity'
				WHEN 'DH1005' THEN 'Productivity'
				WHEN 'DH1006' THEN 'Education'
				WHEN 'DH1007' THEN 'Reading & Reference'
				WHEN 'DH1008' THEN 'Health & Fitness'
				WHEN 'DH1009' THEN 'Other'
				ELSE ZUSAGECATEGORY.ZIDENTIFIER
			END AS 'CATEGORY ID',
			ZUSAGETIMEDITEM.ZTOTALTIMEINSECONDS  AS 'APP USAGE TIME ITEM (SECONDS)',	
			ZUSAGETIMEDITEM.ZTOTALTIMEINSECONDS/60.00 AS 'APP USAGE TIME ITEM (MINUTES)',	
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
			ZUSAGETIMEDITEM.Z_PK AS 'ZUSAGETIMEDITEM TABLE ID'
		FROM ZUSAGETIMEDITEM
		LEFT JOIN ZUSAGECATEGORY ON ZUSAGECATEGORY.Z_PK == ZUSAGETIMEDITEM.ZCATEGORY
		LEFT JOIN ZUSAGEBLOCK ON ZUSAGECATEGORY.ZBLOCK == ZUSAGEBLOCK.Z_PK
		LEFT JOIN ZUSAGE ON ZUSAGEBLOCK.ZUSAGE == ZUSAGE.Z_PK
		LEFT JOIN ZCOREUSER ON ZUSAGE.ZUSER == ZCOREUSER.Z_PK
		LEFT JOIN ZCOREDEVICE ON ZUSAGE.ZDEVICE == ZCOREDEVICE.Z_PK
			''')
	else:
			cursor = db.cursor()
			cursor.execute('''
			SELECT 
				DATETIME(ZUSAGEBLOCK.ZSTARTDATE+978307200,'UNIXEPOCH') AS 'HOUR',
				ZUSAGETIMEDITEM.ZBUNDLEIDENTIFIER AS  'BUNDLE ID',
				ZUSAGETIMEDITEM.ZDOMAIN AS 'DOMAIN',
				CASE ZUSAGECATEGORY.ZIDENTIFIER 
					WHEN 'DH0011' THEN 'Unspecified1'
					WHEN 'DH0012' THEN 'Unspecified2'
					WHEN 'DH0013' THEN 'Unspecified3'
					WHEN 'DH1001' THEN 'Games'
					WHEN 'DH1002' THEN 'Social Networking'
					WHEN 'DH1003' THEN 'Entertainment'
					WHEN 'DH1004' THEN 'Creativity'
					WHEN 'DH1005' THEN 'Productivity'
					WHEN 'DH1006' THEN 'Education'
					WHEN 'DH1007' THEN 'Reading & Reference'
					WHEN 'DH1008' THEN 'Health & Fitness'
					WHEN 'DH1009' THEN 'Other'
					ELSE ZUSAGECATEGORY.ZIDENTIFIER
				END AS 'CATEGORY ID',
				ZUSAGETIMEDITEM.ZTOTALTIMEINSECONDS  AS 'APP USAGE TIME ITEM (SECONDS)',	
				ZUSAGETIMEDITEM.ZTOTALTIMEINSECONDS/60.00 AS 'APP USAGE TIME ITEM (MINUTES)',	
				ZUSAGEBLOCK.ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE AS 'NUMBER OF PICKUPS W/O APP USAGE',	
				ZCOREDEVICE.ZNAME AS 'NAME',
				ZCOREDEVICE.ZIDENTIFIER AS 'DEVICE ID',
				ZCOREDEVICE.ZLOCALUSERDEVICESTATE AS 'LOCAL USER DEVICE STATE',
				ZCOREUSER.ZGIVENNAME AS 'GIVEN NAME',
				ZCOREUSER.ZFAMILYNAME AS 'FAMILY NAME',
				ZCOREUSER.ZFAMILYMEMBERTYPE AS 'FAMILY MEMBER TYPE',
				ZCOREUSER.ZAPPLEID AS 'APPLE ID',
				ZCOREUSER.ZDSID AS 'DSID',
				ZUSAGETIMEDITEM.Z_PK AS 'ZUSAGETIMEDITEM TABLE ID'
			FROM ZUSAGETIMEDITEM
			LEFT JOIN ZUSAGECATEGORY ON ZUSAGECATEGORY.Z_PK == ZUSAGETIMEDITEM.ZCATEGORY
			LEFT JOIN ZUSAGEBLOCK ON ZUSAGECATEGORY.ZBLOCK == ZUSAGEBLOCK.Z_PK
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
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]))

			report = ArtifactHtmlReport('Screentime Timed Items')
			report.start_artifact_report(report_folder, 'Timed Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Domain','Category ID', 'App Usage Time Item in Seconds','App Usage Time Item in Minutes','Number of Pickpus w/o App Usage','Name','Device ID','Local User Device State','Platform','Given Name','Family Name','Family Member Type','AppleID','DSID','Alt DSID','Table ID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Generic by Hour'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			for row in all_rows: 
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]))
					
			report = ArtifactHtmlReport('Screentime Timed Items')
			report.start_artifact_report(report_folder, 'Timed Items')
			report.add_script()
			data_headers = ('Hour','Bundle ID','Domain','Category ID', 'App Usage Time Item in Seconds','App Usage Time Item in Minutes','Number of Pickpus w/o App Usage','Name','Device ID','Local User Device State','Given Name','Family Name','Family Member Type','AppleID','DSID','Table ID')   
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Timed Items'
			tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table foe Screentime Timed Items')

	db.close()
	return      
