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
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_locationDsteps(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
	
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) >= version.parse("10"):
		cursor = db.cursor()
		cursor.execute(
		"""
		SELECT 
		DATETIME(STARTTIME + 978307200, 'UNIXEPOCH') AS "START TIME",
		TIMESTAMP AS "MOVEMENT TIME",
		COUNT AS "COUNT", 
		DISTANCE AS "DISTANCE", 
		RAWDISTANCE AS "RAWDISTANCE",
		FLOORSASCENDED AS "FLOORS ASCENDED",
		FLOORSDESCENDED AS "FLOORS DESCENDED",
		PACE AS "PACE",
		ACTIVETIME AS "ACTIVE TIME",
		FIRSTSTEPTIME AS "FIRST STEP TIME",
		PUSHCOUNT AS "PUSH COUNT",
		WORKOUTTYPE AS "WORKOUT TYPE",
		STEPCOUNTHISTORY.ID AS "STEPCOUNTHISTORY TABLE ID"
		FROM STEPCOUNTHISTORY
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Steps')
			report.start_artifact_report(report_folder, 'Steps', description)
			report.add_script()
			data_headers = ('Start Time','Movement Time','Count','Distance','Raw Distance','Floors Ascended','Floors Descended','Pace','Active Time','First Step Time','Push Count','Workout Type','Table ID')     
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
		cursor.execute(
		"""
		SELECT 
		DATETIME(STARTTIME + 978307200, 'UNIXEPOCH') AS "START TIME",
		TIMESTAMP AS "MOVEMENT TIME",
		COUNT AS "COUNT", 
		DISTANCE AS "DISTANCE", 
		RAWDISTANCE AS "RAWDISTANCE",
		FLOORSASCENDED AS "FLOORS ASCENDED",
		FLOORSDESCENDED AS "FLOORS DESCENDED",
		PACE AS "PACE",
		ACTIVETIME AS "ACTIVE TIME",
		STEPCOUNTHISTORY.ID AS "STEPCOUNTHISTORY TABLE ID"
		FROM STEPCOUNTHISTORY
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Steps')
			report.start_artifact_report(report_folder, 'Steps', description)
			report.add_script()
			data_headers = ('Start Time','Movement Time','Count','Distance','Raw Distance','Floors Ascended','Floors Descended','Pace','Active Time','Table ID')     
			report.write_artifact_data_table(data_headers, data_list, file_found)
			report.end_artifact_report()
			
			tsvname = 'LocationD Steps'
			tsv(report_folder, data_headers, data_list, tsvname)
		else:
			logfunc('No data available for Steps')
	
	elif version.parse(iOSversion) >= version.parse("8"):
		cursor = db.cursor()
		cursor.execute(
		"""
		SELECT 
		DATETIME(STARTTIME + 978307200, 'UNIXEPOCH') AS "START TIME",
		TIMESTAMP AS "MOVEMENT TIME",
		COUNT AS "COUNT", 
		DISTANCE AS "DISTANCE", 
		RAWDISTANCE AS "RAWDISTANCE",
		FLOORSASCENDED AS "FLOORS ASCENDED",
		FLOORSDESCENDED AS "FLOORS DESCENDED",
		STEPCOUNTHISTORY.ID AS "STEPCOUNTHISTORY TABLE ID"
		FROM STEPCOUNTHISTORY		
		""")

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		data_list = []    
		if usageentries > 0:
			for row in all_rows:
				data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
		
			description = ''
			report = ArtifactHtmlReport('LocationD Steps')
			report.start_artifact_report(report_folder, 'Steps', description)
			report.add_script()
			data_headers = ('Start Time','Movement Time','Count','Distance','Raw Distance','Floors Ascended','Floors Descended','Table ID')     
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
	