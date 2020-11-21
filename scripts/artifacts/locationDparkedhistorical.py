import glob
import os
import pathlib
import plistlib
import sqlite3
import json
from packaging import version
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly


def get_locationDparkedhistorical(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("11"):
		logfunc("Unsupported version for RoutineD Parked Historical " + iOSversion)
		return ()

	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()
	cursor.execute("""
	select
	datetime(zrtvehicleeventhistorymo.zdate + 978307200, 'unixepoch'),
	datetime(zrtvehicleeventhistorymo.zlocdate + 978307200, 'unixepoch'),
	zlocuncertainty,
	zidentifier,
	zloclatitude,
	zloclongitude
	from
	zrtvehicleeventhistorymo
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

		description = ''
		report = ArtifactHtmlReport('RoutineD Parked Vehicle Historical')
		report.start_artifact_report(report_folder, 'Parked Vehicle Historical', description)
		report.add_script()
		data_headers = ('Timestamp','Location Date','Location Uncertainty','Identifier','Latitude','Longitude')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'RoutineD Parked Vehicle Historical'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'RoutineD Parked Vehicle Historical'
		timeline(report_folder, tlactivity, data_list, data_headers)
		
		kmlactivity = 'RoutineD Parked Vehicle Historical'
		kmlgen(report_folder, kmlactivity, data_list, data_headers)
	else:
		logfunc('No data available in Routine Parked Vehicle Historical')

	db.close()
	return      
	