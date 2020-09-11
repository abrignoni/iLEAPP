import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_locationDallB(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("11"):
		logfunc("Unsupported version for LocationD App Harvest on iOS " + iOSversion)
	else:
		logfunc(iOSversion)
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
			
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT
	DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP",
	LATITUDE || ", " || LONGITUDE AS "COORDINATES",
	MCC AS "MCC",
	SID AS "SID",
	NID AS "NID",
	BSID AS "BSID",
	ZONEID AS "ZONEID",
	BANDCLASS AS "BANDCLASS",
	CHANNEL AS "CHANNEL",
	PNOFFSET AS "PNOFFSET",
	ALTITUDE AS "ALTITUDE",
	SPEED AS "SPEED",
	COURSE AS "COURSE",
	CONFIDENCE AS "CONFIDENCE",
	HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
	VERTICALACCURACY AS "VERTICAL ACCURACY",
	LATITUDE AS "LATITUDE",
	LONGITUDE AS "LONGITUDE"
	FROM CDMACELLLOCATION
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]))
	
		description = ''
		report = ArtifactHtmlReport('LocationD CDMA Location')
		report.start_artifact_report(report_folder, 'CDMA Location', description)
		report.add_script()
		data_headers = ('Timestamp','Coordinates','MCC','SID','NID','BSID','ZONEID','BANDCLASS','Channel','PNOFFSET','Altitude','Speed','Course','Confidence','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'LocationD CDMA Location'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'LocationD CDMA Location'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for LocationD CDMA Location')
		
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT
	DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP", 
	LATITUDE || ", " || LONGITUDE AS "COORDINATES",
	MCC AS "MCC",
	MNC AS "MNC",
	LAC AS "LAC",
	CI AS "CI",
	UARFCN AS "UARFCN",
	PSC AS "PSC",
	ALTITUDE AS "ALTITUDE",
	SPEED AS "SPEED",
	COURSE AS "COURSE",
	CONFIDENCE AS "CONFIDENCE",
	HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
	VERTICALACCURACY AS "VERTICAL ACCURACY",
	LATITUDE AS "LATITUDE",
	LONGITUDE AS "LONGITUDE"
	FROM CELLLOCATION
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]))
	
		description = ''
		report = ArtifactHtmlReport('LocationD Cell Location')
		report.start_artifact_report(report_folder, 'Cell Location', description)
		report.add_script()
		data_headers = ('Timestamp','Coordinates','MCC','MNC','LAC','CI','UARFCN','PSC','Altitude','Speed','Course','Confidence','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'LocationD Cell Location'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'LocationD Cell Location'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for LocationD Cell Location')

	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT 
	DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP",
	LATITUDE || ", " || LONGITUDE AS "COORDINATES",
	MCC AS "MCC",
	MNC AS "MNC",
	CI AS "CI",
	UARFCN AS "UARFCN",
	PID AS "PID",
	ALTITUDE AS "ALTITUDE",
	SPEED AS "SPEED",
	COURSE AS "COURSE",
	CONFIDENCE AS "CONFIDENCE",
	HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
	VERTICALACCURACY AS "VERTICAL ACCURACY",
	LATITUDE AS "LATITUDE",
	LONGITUDE AS "LONGITUDE"
	FROM LTECELLLOCATION
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
	
		description = ''
		report = ArtifactHtmlReport('LocationD LTE Location')
		report.start_artifact_report(report_folder, 'LTE Location', description)
		report.add_script()
		data_headers = ('Timestamp','Coordinates','MCC','MNC','CI','UARFCN','PID','Altitude','Speed','Course','Confidence','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'LocationD LTE Location'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'LocationD LTE Location'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for LocationD LTE Location')
		

	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT
	DATETIME(TIMESTAMP + 978307200,'UNIXEPOCH') AS "TIMESTAMP",
	LATITUDE || ", " || LONGITUDE AS "COORDINATES",
	MAC AS "MAC",
	CHANNEL AS "CHANNEL",
	INFOMASK AS "INFOMASK",
	SPEED AS "SPEED",
	COURSE AS "COURSE",
	CONFIDENCE AS "CONFIDENCE",
	SCORE AS "SCORE",
	REACH AS "REACH",
	HORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
	VERTICALACCURACY AS "VERTICAL ACCURACY",
	LATITUDE AS "LATITUDE",
	LONGITUDE AS "LONGITUDE"
	FROM WIFILOCATION
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))
	
		description = ''
		report = ArtifactHtmlReport('LocationD WiFi Location')
		report.start_artifact_report(report_folder, 'WiFi Location', description)
		report.add_script()
		data_headers = ('Timestamp','Coordinates','MAC','Channel','Infomask','Speed','Course','Confidence','Score','Reach','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'LocationD WiFi Location'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'LocationD WiFi Location'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for LocationD WiFi Location')
	