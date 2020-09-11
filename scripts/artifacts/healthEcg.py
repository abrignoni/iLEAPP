import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_healthEcg(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT
		DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
		DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
		METADATA_VALUES.NUMERICAL_VALUE AS "ECG AVERAGE HEARTRATE",
		(SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS"
	FROM
	    SAMPLES 
	    LEFT OUTER JOIN
	        METADATA_VALUES 
	        ON METADATA_VALUES.OBJECT_ID = SAMPLES.DATA_ID 
	    LEFT OUTER JOIN
	        METADATA_KEYS 
	        ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID 
	    LEFT OUTER JOIN
	        WORKOUTS 
	        ON WORKOUTS.DATA_ID = SAMPLES.DATA_ID 
	WHERE
	    KEY IS "_HKPrivateMetadataKeyElectrocardiogramHeartRate"
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries == 0:
		logfunc('No data available in table')
	else:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3] ))

		description = ''
		report = ArtifactHtmlReport('Health ECG Avg Heart Rate')
		report.start_artifact_report(report_folder, 'ECG Avg. Heart Rate', description)
		report.add_script()
		data_headers = ('Start Date','End Date','ECG Avg. Heart Rate','Time in Seconds' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Health ECG'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Health ECG'
		timeline(report_folder, tlactivity, data_list, data_headers)
	