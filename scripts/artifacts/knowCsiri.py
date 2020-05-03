import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows 


def get_knowCsiri(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
	ZOBJECT.ZVALUESTRING AS "APP NAME",  
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
	DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
	DATETIME(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') AS "ENTRY CREATION",
	ZOBJECT.ZUUID AS "UUID", 
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
	ZSTREAMNAME =  "/siri/ui" 
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	for row in all_rows:
		data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

	description = ''
	report = ArtifactHtmlReport('KnowledgeC Siri Usage')
	report.start_artifact_report(report_folder, 'KnowledgeC Siri Usage', description)
	report.add_script()
	data_headers = ('App Name','Weekday','GMT Offset','Start','Entry Creation','UUID','ZOBJECT Table ID' )     
	report.write_artifact_data_table(data_headers, data_list, file_found)
	report.end_artifact_report()
	