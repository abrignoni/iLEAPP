import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 

    
def get_knowCact(files_found, report_folder, seeker):
	file_found = str(files_found[0])

	db = sqlite3.connect(file_found)
	cursor = db.cursor()
	cursor.execute(
		'''
	SELECT
	datetime(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
		CASE ZOBJECT.ZSTARTDAYOFWEEK 
		WHEN "1" THEN "Sunday"
		WHEN "2" THEN "Monday"
		WHEN "3" THEN "Tuesday"
		WHEN "4" THEN "Wednesday"
		WHEN "5" THEN "Thursday"
		WHEN "6" THEN "Friday"
		WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	datetime(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
	datetime(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END", 
	ZOBJECT.ZSTREAMNAME, 
	ZOBJECT.ZVALUESTRING,
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ACTIVITYTYPE AS "ACTIVITY TYPE",  
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__TITLE as "TITLE", 
	datetime(ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__EXPIRATIONDATE+978307200,'UNIXEPOCH') as "EXPIRATION DATE",
	ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMRELATEDCONTENTURL as "CONTENT URL",
	datetime(ZSTRUCTUREDMETADATA.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_DATE+978307200,'UNIXEPOCH')  as "CALENDAR DATE",
	datetime(ZSTRUCTUREDMETADATA.ZCOM_APPLE_CALENDARUIKIT_USERACTIVITY_ENDDATE+978307200,'UNIXEPOCH')  as "CALENDAR END DATE"
	FROM ZOBJECT
	left join ZSTRUCTUREDMETADATA on ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
	left join ZSOURCE on ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
	WHERE ZSTREAMNAME is "/app/activity" 
	ORDER BY "ENTRY CREATION"'''
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries > 0: 
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))

		description = ''
		report = ArtifactHtmlReport('KnowledgeC App Activity')
		report.start_artifact_report(report_folder, 'App Activity', description)
		report.add_script()
		data_headers = ('Entry Creation','Day of the Week','Start','End','ZSTREAMNAME', 'ZVALUESTRING', 'Activity Type', 'Title', 'Expiration Date', 'Content URL', 'Calendar Date', 'Calendar End Date' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'KnowledgeC App Activity'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'KnowledgeC App Activity'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in table')
		
	db.close()
	return 

