import glob
import os
import pathlib
import plistlib
import sqlite3
import json
from packaging import version
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_knowCcarplaycon(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("11"):
		logfunc("Unsupported version for KnowledgC Car Play Connections" + iOSversion)
		return ()

	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
		DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
		DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
		CASE ZOBJECT.ZVALUEINTEGER
			WHEN '0' THEN 'DISCONNECTED' 
			WHEN '1' THEN 'CONNECTED' 
		END "CARPLAY CONNECTED",
		(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",
		(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE)/60.00 AS "USAGE IN MINUTES",  
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
		ZSTREAMNAME is "/carplay/isConnected"	
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

		description = ''
		report = ArtifactHtmlReport('KnowledgeC Car Play Connections')
		report.start_artifact_report(report_folder, 'Car Play Connections', description)
		report.add_script()
		data_headers = ('Start','End','Car Play Connected','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation','UUID','Zobject Table ID')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'KnowledgeC Car Play Connections'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'KnowledgeC Car Play Connections'
		timeline(report_folder, tlactivity, data_list)
	else:
		logfunc('No data available in table')

	db.close()
	return      
	