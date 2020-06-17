import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows


def get_aggDictpasscodetype(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
	DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
	KEY AS "KEY",
	CASE 
		WHEN VALUE=-1 THEN '6-Digit'
		WHEN VALUE=0 THEN 'No Passcode'
		WHEN VALUE=1 THEN '4-Digit'
		WHEN VALUE=2 THEN 'Custom Alphanumeric'
		WHEN VALUE=3 THEN 'Custom Numeric'
		ELSE "N/A"
	END "VALUE"
	FROM
	SCALARS
	where key like 'com.apple.passcode.PasscodeType%'
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	for row in all_rows:
		data_list.append((row[0], row[1], row[2]))

	description = ''
	report = ArtifactHtmlReport('Aggregate Dictionary Passcode Type')
	report.start_artifact_report(report_folder, 'Passcode Type', description)
	report.add_script()
	data_headers = ('Day','Key','Value')     
	report.write_artifact_data_table(data_headers, data_list, file_found)
	report.end_artifact_report()
	
	tsvname = 'Agg Dict Dictionary Passcode Type'
	tsv(report_folder, data_headers, data_list, tsvname)
	