import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from packaging import version

def get_locationDappharvest(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("11"):
		logfunc("Unsupported version for LocationD App Harvest on iOS " + iOSversion)
		return ()
	
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
	DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP",
	BUNDLEID AS "BUNDLE ID",
	LATITUDE || ", " || LONGITUDE AS "COORDINATES",
	ALTITUDE AS "ALTITUDE",
	HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
	VERTICALACCURACY AS "VERTICAL ACCURACY",
	STATE AS "STATE",
	AGE AS "AGE",
	ROUTINEMODE AS "ROUTINE MODE",
	LOCATIONOFINTERESTTYPE AS "LOCATION OF INTEREST TYPE",
	HEX(SIG) AS "SIG (HEX)",
	LATITUDE AS "LATITUDE",
	LONGITUDE AS "LONGITUDE",
	SPEED AS "SPEED",
	COURSE AS "COURSE",
	CONFIDENCE AS "CONFIDENCE"
	FROM APPHARVEST
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]))
	
		description = ''
		report = ArtifactHtmlReport('LocationD App Harvest')
		report.start_artifact_report(report_folder, 'App Harvest', description)
		report.add_script()
		data_headers = ('Timestamp','Bundle ID','Coordinates','Altitude','Horizontal Accuracy','Vertical Accuracy','State','Age','Routine Mode','Location of Interest Type','Sig (HEX)','Latitude','Longitude','Speed','Course','Confidence')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'LocationD Cell App Harvest'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'LocationD Cell App Harvest'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for LocationD App Harvest')
	
	db.close()
	return 
	