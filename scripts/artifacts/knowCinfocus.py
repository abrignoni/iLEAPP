import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_knowCinfocus(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("12"):
		cursor = db.cursor()
		cursor.execute('''
		SELECT
				DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
				DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
				ZOBJECT.ZVALUESTRING AS "BUNDLE ID", 
				ZSTRUCTUREDMETADATA .Z_DKAPPLICATIONMETADATAKEY__LAUNCHREASON AS "LAUNCH REASON",
				(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",
				(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE)/60.00 AS "USAGE IN MINUTES",
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
			FROM ZOBJECT
			LEFT JOIN
		         ZSTRUCTUREDMETADATA 
		         ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
			WHERE ZSTREAMNAME IS "/app/inFocus"
			''')
	else:
			cursor = db.cursor()
			cursor.execute('''
			SELECT
				DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
				DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
				ZOBJECT.ZVALUESTRING AS "BUNDLE ID", 
				(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) AS "USAGE IN SECONDS",
				(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE)/60.00 AS "USAGE IN MINUTES",
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
				ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
			FROM ZOBJECT
			WHERE ZSTREAMNAME IS "/app/inFocus"
					''')

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []
		if version.parse(iOSversion) >= version.parse("12"):
					
			for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

			report = ArtifactHtmlReport('KnowledgeC Application In Focus')
			report.start_artifact_report(report_folder, 'App In Focus')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Launch Reason', 'Usage in Seconds', 'Usage in Minutes','Day of Week','GMT Offset','Entry Creation','UUID','ZOBJECT Table ID')  
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application in Focus'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application in Focus'
			timeline(report_folder, tlactivity, data_list)
		else:
			for row in all_rows:    
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
					
			report = ArtifactHtmlReport('KnowledgeC Application In Focus')
			report.start_artifact_report(report_folder, 'App in Focus')
			report.add_script()
			data_headers = ('Start','End','Bundle ID','Usage in Seconds','Usage in Minutes','Day of Week','GMT Offset','Entry Creation','ZOBJECT Table ID' ) 
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'KnowledgeC Application in Focus'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'KnowledgeC Application in Focus'
			timeline(report_folder, tlactivity, data_list)
	else:
		logfunc('No data available in table')

	db.close()
	return      
