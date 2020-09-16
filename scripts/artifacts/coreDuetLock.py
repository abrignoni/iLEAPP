import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_coreDuetLock(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT 
		DATETIME(ZCREATIONDATE+978307200,"UNIXEPOCH") AS "CREATE TIME",
		TIME(ZLOCALTIME,"UNIXEPOCH") AS "LOCAL DEVICE TIME",
		TIME(ZCREATIONDATE-ZLOCALTIME,"UNIXEPOCH") AS "TIME ZONE",
		CASE ZLOCKSTATE
		    WHEN "0" THEN "UNLOCKED"
		    WHEN "1" THEN "LOCKED"
		END "LOCK STATE"
	FROM ZCDDMSCREENLOCKEVENT	
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		data_list = []
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3] ))

		description = ''
		report = ArtifactHtmlReport('CoreDuet Lock State')
		report.start_artifact_report(report_folder, 'Lock State', description)
		report.add_script()
		data_headers = ('Create Time','Local Device Time','Time Zone','Lock State' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'CoreDuet Lock State'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'CoreDuet Lock State'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in table')
	