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


def get_bluetoothPaired(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()

	cursor.execute("""
	select 
	Uuid,
	Name,
	NameOrigin,
	Address,
	ResolvedAddress,
	LastSeenTime,
	LastConnectionTime
	from 
	PairedDevices
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4],row[6]))
	
		description = ''
		report = ArtifactHtmlReport('Bluetooth Paired LE')
		report.start_artifact_report(report_folder, 'Paired LE', description)
		report.add_script()
		data_headers = ('UUID','Name','Name Origin','Address','Resolved Address','Last Connection Time' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Bluetooth Paired LE'
		tsv(report_folder, data_headers, data_list, tsvname)

	else:
		logfunc('No data available for Bluetooth Paired LE')
	
	db.close()
	return 
	
