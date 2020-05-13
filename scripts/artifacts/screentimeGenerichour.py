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

def get_screentimeGenerichour(files_found, report_folder, seeker):
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
			DISTINCT
			DATETIME(ZUSAGEBLOCK.ZSTARTDATE+978307200,'UNIXEPOCH') AS 'HOUR',
			ZUSAGEBLOCK.ZSCREENTIMEINSECONDS AS 'SCREENTIME (SECONDS)',
			ZUSAGEBLOCK.ZSCREENTIMEINSECONDS/60.00 AS 'SCREENTIME (MINUTES)',	
			ZCOREUSER.ZGIVENNAME AS 'GIVEN NAME',
			ZCOREUSER.ZFAMILYNAME AS 'FAMILY NAME',
			ZCOREDEVICE.ZNAME AS 'NAME',
			CASE ZCOREDEVICE.ZPLATFORM
				WHEN 0 THEN 'Unknown'
				WHEN 1 THEN 'macOS'
				WHEN 2 THEN 'iOS'
				WHEN 4 THEN 'Apple Watch'
				ELSE ZPLATFORM
			END AS PLATFORM,
			ZCOREDEVICE.ZIDENTIFIER AS 'DEVICE ID',
			ZCOREDEVICE.ZLOCALUSERDEVICESTATE AS 'LOCAL USER DEVICE STATE',
			DATETIME(ZUSAGEBLOCK.ZLONGESTSESSIONSTARTDATE+978307200,'UNIXEPOCH') AS 'LONGEST SESSION START',
			DATETIME(ZUSAGEBLOCK.ZLONGESTSESSIONENDDATE+978307200,'UNIXEPOCH') AS 'LONGEST SESSION END',
			DATETIME(ZUSAGEBLOCK.ZLASTEVENTDATE+978307200,'UNIXEPOCH') AS 'LAST EVENT DATE',
			(ZLONGESTSESSIONENDDATE-ZLONGESTSESSIONSTARTDATE) AS 'LONGEST SESSION TIME (SECONDS)',
			(ZLONGESTSESSIONENDDATE-ZLONGESTSESSIONSTARTDATE)/60.00 AS 'LONGEST SESSION TIME (MINUTES)',
			ZCOREUSER.ZFAMILYMEMBERTYPE AS 'FAMILY MEMBER TYPE',
			ZCOREUSER.ZAPPLEID AS 'APPLE ID',
			ZCOREUSER.ZDSID AS 'DSID',
			ZCOREUSER.ZALTDSID AS 'ALT DSID'
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
				DISTINCT
				DATETIME(ZUSAGEBLOCK.ZSTARTDATE+978307200,'UNIXEPOCH') AS 'HOUR',
				ZUSAGEBLOCK.ZSCREENTIMEINSECONDS AS 'SCREENTIME (SECONDS)',
				ZUSAGEBLOCK.ZSCREENTIMEINSECONDS/60.00 AS 'SCREENTIME (MINUTES)',	
				ZCOREUSER.ZGIVENNAME AS 'GIVEN NAME',
				ZCOREUSER.ZFAMILYNAME AS 'FAMILY NAME',
				ZCOREDEVICE.ZNAME AS 'NAME',
				ZCOREDEVICE.ZIDENTIFIER AS 'DEVICE ID',
				ZCOREDEVICE.ZLOCALUSERDEVICESTATE AS 'LOCAL USER DEVICE STATE',
				DATETIME(ZUSAGEBLOCK.ZLONGESTSESSIONSTARTDATE+978307200,'UNIXEPOCH') AS 'LONGEST SESSION START',
				DATETIME(ZUSAGEBLOCK.ZLONGESTSESSIONENDDATE+978307200,'UNIXEPOCH') AS 'LONGEST SESSION END',
				DATETIME(ZUSAGEBLOCK.ZLASTEVENTDATE+978307200,'UNIXEPOCH') AS 'LAST EVENT DATE',
				(ZLONGESTSESSIONENDDATE-ZLONGESTSESSIONSTARTDATE) AS 'LONGEST SESSION TIME (SECONDS)',
				(ZLONGESTSESSIONENDDATE-ZLONGESTSESSIONSTARTDATE)/60.00 AS 'LONGEST SESSION TIME (MINUTES)',
				ZCOREUSER.ZFAMILYMEMBERTYPE AS 'FAMILY MEMBER TYPE',
				ZCOREUSER.ZAPPLEID AS 'APPLE ID',
				ZCOREUSER.ZDSID AS 'DSID'
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

			report = ArtifactHtmlReport('Screentime Generic by Hour')
			report.start_artifact_report(report_folder, 'Generic by Hour')
			report.add_script()
			data_headers = ('Hour','Screentime in Seconds','Screentime in Minutes','Given Name', 'Family Name','Name','Platform','Device ID','Local User Device State','Longest Session Start','Longest Session End','Last Event Data','Longest Session Time in Seconds','Longest Session Time in Minutes','Family Member Type','Apple ID','DSID','Alt DSID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Generic by Hour'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			for row in all_rows: 
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))
					
			report = ArtifactHtmlReport('Screentime Generic by Hour')
			report.start_artifact_report(report_folder, 'Generic Hour')
			report.add_script()
			data_headers = ('Hour','Screentime in Seconds','Screentime in Minutes','Given Name', 'Family Name','Name','Device ID','Local User Device State','Longest Session Start','Longest Session End','Last Event Data','Longest Session Time in Seconds','Longest Session Time in Minutes','Family Member Type','Apple ID','DSID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'Screentime Generic by Hour'
			tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table foe Screentime Generic by Hour')

	db.close()
	return      
