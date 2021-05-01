import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_safariTabs(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()

	cursor.execute("""
	select
	datetime(last_viewed_time+978307200,'unixepoch'), 
	title, 
	url, 
	user_visible_url, 
	opened_from_link, 
	private_browsing
	from
	tabs
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
	
		description = ''
		report = ArtifactHtmlReport('Safari Browser Tabs')
		report.start_artifact_report(report_folder, 'Tabs', description)
		report.add_script()
		data_headers = ('Last Viewed Time','Title','URL','User Visible URL','Opened from Link', 'Private Browsing')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Safari Browser Tabs'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Safari Browser Tabs'
		timeline(report_folder, tlactivity, data_list, data_headers)
		
	else:
		logfunc('No data available in table')
	
	db.close()
	return 
	