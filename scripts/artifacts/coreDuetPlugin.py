import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_coreDuetPlugin(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT 
	DATETIME(ZCREATIONDATE+978307200,'UNIXEPOCH') AS "TIMESTAMP",
	TIME(ZCREATIONDATE-ZLOCALTIME,'UNIXEPOCH') AS "TIME ZONE", 
	CASE ZCABLESTATE
	    WHEN "0" THEN "UNPLUGGED"
	    WHEN "1" THEN "PLUGGED IN"
	END "CABLE STATE"
	FROM ZCDDMPLUGINEVENT	
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
		report = ArtifactHtmlReport('CoreDuet Plugged In')
		report.start_artifact_report(report_folder, 'Plugged In', description)
		report.add_script()
		data_headers = ('Timestamp','Time Zone','Cable State' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'CoreDuet Plugged In'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Coreduet Plugged In'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in table')