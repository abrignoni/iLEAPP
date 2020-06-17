import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 


def get_bluetoothOther(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
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
			data_list.append((row[0], row[1], row[2], row[3]))
	
		description = ''
		report = ArtifactHtmlReport('Bluetooth Other')
		report.start_artifact_report(report_folder, 'Other', description)
		report.add_script()
		data_headers = ('Name','Address','Last Seen Time','UUID' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Bluetooth Other'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available for Bluetooth Other')
	
	db.close()
	return 
	