import glob
import os
import sys
import stat
import pathlib
import plistlib
import sqlite3
import json
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_locationDsteps(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = open_sqlite_db_readonly(file_found)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("10"):
		cursor = db.cursor()
		cursor.execute("""
		select 
		datetime(starttime + 978307200, 'unixepoch') as "start time",
		timestamp,
		count, 
		distance, 
		rawdistance,
		floorsascended,
		floorsdescended,
		pace,
		activetime,
		firststeptime,
		pushcount,
		workouttype
		from stepcounthistory
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Steps')
			report.start_artifact_report(report_folder, 'Steps', description)
			report.add_script()
			data_headers = ('Start Time','Movement Time','Count','Distance','Raw Distance','Floors Ascended','Floors Descended','Pace','Active Time','First Step Time','Push Count','Workout Type')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD Steps'
			tsv(report_folder, data_headers, data_list, tsvname)
			
			tlactivity = 'LocationD Steps'
			timeline(report_folder, tlactivity, data_list, data_headers)
		else:
			logfunc('No data available for Steps')
			
	elif version.parse(iOSversion) >= version.parse("9"):
		cursor = db.cursor()
		cursor.execute("""
		select 
		datetime(starttime + 978307200, 'unixepoch'),
		timestamp,
		count, 
		distance, 
		rawdistance,
		floorsascended,
		floorsdescended,
		pace,
		activetime
		from stepcounthistory
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Steps')
			report.start_artifact_report(report_folder, 'Steps', description)
			report.add_script()
			data_headers = ('Start Time','Movement Time','Count','Distance','Raw Distance','Floors Ascended','Floors Descended','Pace','Active Time')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD Steps'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			logfunc('No data available for Steps')
	
	elif version.parse(iOSversion) >= version.parse("8"):
		cursor = db.cursor()
		cursor.execute("""
		select 
		datetime(starttime + 978307200, 'unixepoch'),
		timestamp,
		count, 
		distance, 
		rawdistance,
		floorsascended,
		floorsdescended
		from stepcounthistory		
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Steps')
			report.start_artifact_report(report_folder, 'Steps', description)
			report.add_script()
			data_headers = ('Start Time','Movement Time','Count','Distance','Raw Distance','Floors Ascended','Floors Descended')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD Steps'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			logfunc('No data available for Steps')

	else:
		logfunc('No data available for Steps')
	
	db.close()
	return 
	