import base64
import json
import sqlite3
import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows


def get_geodApplications(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
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
			data_list.append((row[0], row[1], row[2]))
			description = ''
		report = ArtifactHtmlReport('Geolocation')
		report.start_artifact_report(report_folder, 'Applications', description)
		report.add_script()
		data_headers = ("Count ID", "Application", "Creation Time")
		report.write_artifact_data_table(data_headers, data_list, file_found, html_escape = False)
		report.end_artifact_report()

		tsvname = 'Geolocation Applications'
		tsv(report_folder, data_headers, data_list, tsvname)

	else:
		logfunc('No data available for Geolocation Applications')

	db.close()
	return
