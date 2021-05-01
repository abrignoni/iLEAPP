import base64
import json
import sqlite3
import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_geodApplications(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()
	cursor.execute(
	"""
	SELECT count_type, app_id, createtime
	FROM mkcount
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[2], row[0], row[1] ))
			description = ''
		report = ArtifactHtmlReport('Geolocation')
		report.start_artifact_report(report_folder, 'Applications', description)
		report.add_script()
		data_headers = ("Creation Time", "Count ID", "Application")
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape = False)
		report.end_artifact_report()

		tsvname = 'Geolocation Applications'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Geolocation Applications'
		timeline(report_folder, tlactivity, data_list, data_headers)

	else:
		logfunc('No data available for Geolocation Applications')

	db.close()
	return
	
