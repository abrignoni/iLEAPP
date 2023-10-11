import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_safariWebsearch(files_found, report_folder, seeker, wrap_text, timezone_offset):
	for file_found in files_found:
		file_found = str(file_found)
		
		if file_found.endswith('History.db'):
			db = open_sqlite_db_readonly(file_found)
			cursor = db.cursor()
		
			cursor.execute("""
			select
			datetime(history_visits.visit_time+978307200,'unixepoch') ,
			history_items.url,
			history_items.visit_count,
			history_visits.title,
			case history_visits.origin
			when 1 then "icloud synced"
			when 0 then "visited local device"
			else history_visits.origin
			end "icloud sync",
			history_visits.load_successful,
			history_visits.id,
			history_visits.redirect_source,
			history_visits.redirect_destination
			from history_items, history_visits 
			where history_items.id = history_visits.history_item
			and history_items.url like '%search?q=%'
			"""
			)
		
			all_rows = cursor.fetchall()
			usageentries = len(all_rows)
			
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			search = row[1].split('search?q=')[1].split('&')[0]
			search = search.replace('+', ' ')
			data_list.append((row[0], search, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
	
		description = ''
		report = ArtifactHtmlReport('Safari Browser')
		report.start_artifact_report(report_folder, 'Search Terms', description)
		report.add_script()
		data_headers = ('Visit Time','Search Term','URL','Visit Count','Title','iCloud Sync','Load Successful','Visit ID','Redirect Source','Redirect Destination' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Safari Web Search'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Safari Web Search'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in table')
	
	db.close()
	return 

__artifacts__ = {
    "safariWebsearch": (
        "Safari Browser",
        ('**/Safari/History.db*'),
        get_safariWebsearch)
}