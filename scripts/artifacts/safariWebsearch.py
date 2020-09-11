import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_safariWebsearch(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
		DATETIME(HISTORY_VISITS.VISIT_TIME+978307200,'UNIXEPOCH') AS "VISIT TIME",
		HISTORY_ITEMS.URL AS "URL",
		HISTORY_ITEMS.VISIT_COUNT AS "VISIT COUNT",
		HISTORY_VISITS.TITLE AS "TITLE",
		CASE HISTORY_VISITS.ORIGIN
			WHEN 1 THEN "ICLOUD SYNCED DEVICE"
			WHEN 0 THEN "VISITED FROM THIS DEVICE"
			ELSE HISTORY_VISITS.ORIGIN
		END "ICLOUD SYNC",
		HISTORY_VISITS.LOAD_SUCCESSFUL AS "LOAD SUCCESSFUL",
		HISTORY_VISITS.id AS "VISIT ID",
		HISTORY_VISITS.REDIRECT_SOURCE AS "REDIRECT SOURCE",
		HISTORY_VISITS.REDIRECT_DESTINATION AS "REDIRECT DESTINATION",
		HISTORY_VISITS.ID AS "HISTORY ITEM ID"
	FROM HISTORY_ITEMS
	LEFT OUTER JOIN HISTORY_VISITS ON HISTORY_ITEMS.ID == HISTORY_VISITS.HISTORY_ITEM
	WHERE HISTORY_ITEMS.URL like '%search?q=%'
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			search = row[1].split('search?q=')[1].split('&')[0]
			search = search.replace('+', ' ')
			data_list.append((row[0], search, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
	
		description = ''
		report = ArtifactHtmlReport('Safari Browser')
		report.start_artifact_report(report_folder, 'Search Terms', description)
		report.add_script()
		data_headers = ('Visit Time','Search Term','URL','Visit Count','Title','iCloud Sync','Load Successful','Visit ID','Redirect Source','Redirect Destination','History Item ID' )     
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
	