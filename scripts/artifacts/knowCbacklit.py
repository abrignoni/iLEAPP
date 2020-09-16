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


def get_knowCbacklit(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute(
		"""
			SELECT
				DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
				DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
				CASE ZOBJECT.ZVALUEINTEGER
					WHEN '0' THEN 'NO' 
					WHEN '1' THEN 'YES' 
				END "SCREEN IS BACKLIT",
				(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",
				(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE)/60.00 AS "USAGE IN MINUTES",  
				ZSOURCE.ZDEVICEID AS "DEVICE ID (HARDWARE UUID)",
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
				ZSTREAMNAME is "/display/isBacklit"	
		""")
	elif version.parse(iOSversion) == version.parse("11"):
		cursor = db.cursor()
		cursor.execute(
		"""
		SELECT
			CASE ZOBJECT.ZVALUEINTEGER
				WHEN '0' THEN 'NO' 
				WHEN '1' THEN 'YES' 
			END "SCREEN IS BACKLIT",
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
			DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
			DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
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
			ZSTREAMNAME is "/display/isBacklit"
		""")
	else:
		logfunc("Unsupported version for KnowledgC Backlit" + iOSversion)
		return ()
	
	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("12"):
					
			for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

			report = ArtifactHtmlReport('KnowledgeC Device is Backlit')
			report.start_artifact_report(report_folder, 'Device is Backlit')
			report.add_script()
			data_headers = ('Start','End','Screen is Backlit','Usage in Seconds','Usage in Minutes','Hardware UUID','Day of Week','GMT Offset','Entry Creation','UUID','ZOBJECT Table ID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Device is Backlit'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Device is Backlit'
			timeline(report_folder, tlactivity, data_list, data_headers)
			
		elif version.parse(iOSversion) == version.parse("11"):
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
					
			report = ArtifactHtmlReport('KnowledgeC Device is Backlit')
			report.start_artifact_report(report_folder, 'Device is Backlit')
			report.add_script()
			data_headers = ('Screen is Backlit','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Start','End','Entry Creation','UUID','ZOBJECT Table ID' ) 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Device is Backlit'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Device is Backlit'
			timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in table')

	db.close()
	return      

	