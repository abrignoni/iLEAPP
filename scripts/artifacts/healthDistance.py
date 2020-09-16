import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_healthDistance(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT
		DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
		DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
		QUANTITY AS "DISTANCE IN METERS",
		QUANTITY*3.28084 AS "DISTANCE IN FEET",
		(SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS",
		SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
	FROM
	   SAMPLES 
	   LEFT OUTER JOIN
	      QUANTITY_SAMPLES 
	      ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
	   LEFT OUTER JOIN
	      CORRELATIONS 
	      ON SAMPLES.DATA_ID = CORRELATIONS.OBJECT 
	WHERE
	   SAMPLES.DATA_TYPE = 8 
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries == 0:
		logfunc('No data available in table')
	else:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5] ))

		description = ''
		report = ArtifactHtmlReport('Health Distance')
		report.start_artifact_report(report_folder, 'Distance', description)
		report.add_script()
		data_headers = ('Start Date','End Date','Distance in Meters','Distance in Feet','Time in Seconds','Samples Table ID' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Health Distance'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Health Distance'
		timeline(report_folder, tlactivity, data_list, data_headers)
	