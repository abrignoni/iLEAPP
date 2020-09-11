import glob
import os
import pathlib
import plistlib
import sqlite3
import json
from packaging import version
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 


def get_locationDparkedhistorical(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	if version.parse(iOSversion) < version.parse("11"):
		logfunc("Unsupported version for RoutineD Parked Historical " + iOSversion)
		return ()

	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
		   DATETIME(ZRTVEHICLEEVENTHISTORYMO.ZDATE + 978307200, 'UNIXEPOCH') AS "DATE",
		   DATETIME(ZRTVEHICLEEVENTHISTORYMO.ZLOCDATE + 978307200, 'UNIXEPOCH') AS "LOCATION DATE",
		   ZLOCLATITUDE || ", " || ZLOCLONGITUDE AS "COORDINATES",
		   ZLOCUNCERTAINTY AS "LOCATION UNCERTAINTY",
		   ZIDENTIFIER AS "IDENTIFIER",
		   ZLOCLATITUDE AS "LATITUDE",
		   ZLOCLONGITUDE AS "LONGITUDE",
		   ZRTVEHICLEEVENTHISTORYMO.Z_PK AS "ZRTLEARNEDVISITMO TABLE ID" 
		FROM
		   ZRTVEHICLEEVENTHISTORYMO
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	if usageentries > 0:
		data_list = []    
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

		description = ''
		report = ArtifactHtmlReport('RoutineD Parked Vehicle Historical')
		report.start_artifact_report(report_folder, 'Parked Vehicle Historical', description)
		report.add_script()
		data_headers = ('Date','Location Date','Coordinates','Location Uncertainty','Identifier','Latitude','Longitude','Table ID')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'RoutineD Parked Vehicle Historical'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'RoutineD Parked Vehicle Historical'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available in Routine Parked Vehicle Historical')

	db.close()
	return      
	