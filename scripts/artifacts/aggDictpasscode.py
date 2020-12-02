import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_aggDictpasscode(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()

	cursor.execute("""
	select
	date(dayssince1970*86400, 'unixepoch'),
	key,
	value
	from
	scalars
	where key like 'com.apple.passcode.numpasscode%'
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []
	if usageentries > 0:    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2]))

		description = ''
		report = ArtifactHtmlReport('Aggregate Dictionary Passcode State')
		report.start_artifact_report(report_folder, 'Passcode State', description)
		report.add_script()
		data_headers = ('Day','Key','Value')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Agg Dict Dictionary Passcode State'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Aggregate Dictionary Passcode State'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc("No Agg Dict Dictionary Data available")
		