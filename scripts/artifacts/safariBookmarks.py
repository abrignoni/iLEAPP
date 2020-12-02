import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_safariBookmarks(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()

	cursor.execute("""
	SELECT
		title,
		url,
		hidden
	FROM
	bookmarks
			""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2]))
	
		description = ''
		report = ArtifactHtmlReport('Safari Browser Bookmarks')
		report.start_artifact_report(report_folder, 'Bookmarks', description)
		report.add_script()
		data_headers = ('Title','URL','Hidden')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Safari Browser Bookmarks'
		tsv(report_folder, data_headers, data_list, tsvname)
		
	else:
		logfunc('No data available in table')
	
	db.close()
	return 
	