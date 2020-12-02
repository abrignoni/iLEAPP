import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_bluetoothOther(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
	Name,
	Address,
	LastSeenTime,
	Uuid
	FROM
	OtherDevices
	order by Name desc
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0], row[1], row[3]))
	
		description = ''
		report = ArtifactHtmlReport('Bluetooth Other LE')
		report.start_artifact_report(report_folder, 'Other LE', description)
		report.add_script()
		data_headers = ('Name','Address','UUID' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Bluetooth Other LE'
		tsv(report_folder, data_headers, data_list, tsvname)

		
	else:
		logfunc('No data available for Bluetooth Other')
	
	db.close()
	return 
	
