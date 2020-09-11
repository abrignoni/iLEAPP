import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_locationDcdmaloc1(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
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
	
	db.close()
	return 
	