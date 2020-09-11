import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_healthHr(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT
		DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "DATE",
		ORIGINAL_QUANTITY AS "HEART RATE", 
		UNIT_STRINGS.UNIT_STRING AS "UNITS",
		QUANTITY AS "QUANTITY",
		SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
	FROM
	   SAMPLES 
	   LEFT OUTER JOIN
	      QUANTITY_SAMPLES 
	      ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
	   LEFT OUTER JOIN
	      UNIT_STRINGS 
	      ON QUANTITY_SAMPLES.ORIGINAL_UNIT = UNIT_STRINGS.ROWID 
	WHERE
	   SAMPLES.DATA_TYPE = 5
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries == 0:
			logfunc('No data available in table')
	else:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4] ))

		description = ''
		report = ArtifactHtmlReport('Health Heart Rate')
		report.start_artifact_report(report_folder, 'Heart Rate', description)
		report.add_script()
		data_headers = ('Date','Heart Rate','Units','Quantity','Samples Table ID' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Health HR'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Health HR'
		timeline(report_folder, tlactivity, data_list, data_headers)
	