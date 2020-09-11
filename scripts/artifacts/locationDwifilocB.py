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


def get_locationDwifilocB(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
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
	
	db.close()
	return 
	