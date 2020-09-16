import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_knowClocked(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
	DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
	DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
	CASE ZOBJECT.ZVALUEINTEGER
	WHEN '0' THEN 'UNLOCKED' 
	WHEN '1' THEN 'LOCKED' 
	END "IS LOCKED",
	(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",  
	CASE ZOBJECT.ZSTARTDAYOFWEEK 
	WHEN "1" THEN "Sunday"
	WHEN "2" THEN "Monday"
	WHEN "3" THEN "Tuesday"
	WHEN "4" THEN "Wednesday"
	WHEN "5" THEN "Thursday"
	WHEN "6" THEN "Friday"
	WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
	DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
	DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END",
	DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
	ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
	FROM
	ZOBJECT 
	LEFT JOIN
	ZSTRUCTUREDMETADATA 
	ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
	LEFT JOIN
	ZSOURCE 
	ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
	WHERE
	ZSTREAMNAME LIKE "/device/isLocked"
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries > 0:    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

		description = ''
		report = ArtifactHtmlReport('KnowledgeC Device Locked')
		report.start_artifact_report(report_folder, 'Device Locked', description)
		report.add_script()
		data_headers = ('Start','End','Is Locked?','Usage in Seconds','Day of the Week','GMT Offset','Entry Creation', 'ZOBJECT Table ID' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'KnowledgeC Device Locked'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'KnowledgeC Device Locked'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for KnowledgeC Device Locked')
	
