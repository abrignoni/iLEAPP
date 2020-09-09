import gzip
import re
import os
import shutil
import sqlite3
from pathlib import Path
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_powerlogGZ(files_found, report_folder, seeker):
	iOSversion = scripts.artifacts.artGlobals.versionf
	
	logfunc('Unzipped Powerlog databases:')
	for file_found in files_found:
		file_found = str(file_found)
		filename = Path(file_found)
		ungzipedfile= Path(filename.parent,filename.stem)
		with gzip.open(file_found, 'rb') as f_in:
			with open(ungzipedfile, 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)
				logfunc(str(filename.stem))
		
			if version.parse(iOSversion) >= version.parse("9"):
				db = sqlite3.connect(ungzipedfile)
				cursor = db.cursor()
				cursor.execute('''
				SELECT
					DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
					DATETIME(TIMESTAMPLOGGED, 'UNIXEPOCH') AS "TIMESTAMP LOGGED",
					APPLICATIONNAME AS "APPLICATION NAME / BUNDLE ID",
					ASSERTIONID AS "ASERTION ID",
					ASSERTIONNAME AS "ASSERTION NAME",
					AUDIOROUTE AS "AUDIO ROUTE",
					MIRRORINGSTATE AS "MIRRORING STATE",
					OPERATION,
					PID,
					ID AS "PLAUDIOAGENT_EVENTPOINT_AUDIOAPP TABLE ID" 
					FROM
					PLAUDIOAGENT_EVENTPOINT_AUDIOAPP
				''')
				
				all_rows = cursor.fetchall()
				usageentries = len(all_rows)
				if usageentries > 0:
					data_list1 = []
					if version.parse(iOSversion) >= version.parse("9"):
						for row in all_rows:
							data_list1.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
						
						report = ArtifactHtmlReport('Powerlog Audio Routing via App')
						report.start_artifact_report(report_folder, 'Audio Routing')
						report.add_script()
						data_headers = ('Timestamp','Timestamped Logged','Bundle ID','Assertion Name','Audio Route','Mirroring State','Operation','PID', 'Audio App Table ID' )   
						report.write_artifact_data_table(data_headers, data_list1, file_found)
						report.end_artifact_report()
						
						tsvname = 'Powerlog Audio Routing via App from backup named ' + filename.stem  
						tsv(report_folder, data_headers, data_list1, tsvname)
						
						tlactivity = 'Powerlog Audio Routing via App from '+ filename.stem
						timeline(report_folder, tlactivity, data_list1)
		
'''
	if len(data_list) > 0:
		description = 'Tile app log recorded langitude and longitude coordinates.'
		report = ArtifactHtmlReport('Locations')
		report.start_artifact_report(report_folder, 'Tile App Geolocation Logs', description)
		report.add_script()
		data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Row Number', 'Source File' )     
		report.write_artifact_data_table(data_headers, data_list, head_tail[0])
		report.end_artifact_report()
		
		tsvname = 'Tile App Lat Long'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Tile App Lat Long'
		timeline(report_folder, tlactivity, data_list)
'''	
		