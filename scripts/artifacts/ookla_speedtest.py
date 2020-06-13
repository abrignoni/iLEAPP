import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 


def get_ooklaSpeedtest(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
		datetime(("ZDATE")+strftime('%s', '2001-01-01 00:00:00'), 'unixepoch') as 'Date',
		"ZEXTERNALIP" as 'External IP Address',
		"ZINTERNALIP" as 'Internal IP Address',
		"ZCARRIERNAME" as 'Carrier Name',
		"ZISP" as 'ISP',
		"ZWIFISSID" as 'Wifi SSID',
		"ZWANTYPE" as 'WAN Type',
		"ZDEVICEMODEL" as 'Device Model'
	FROM ZSPEEDTESTRESULT
	
	ORDER BY "ZDATE" DESC	
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
	
		description = ''
		report = ArtifactHtmlReport('Ookla Speedtest')
		report.start_artifact_report(report_folder, 'Ookla Speedtest', description)
		report.add_script()
		data_headers = ('Date','External IP Address','Internal IP Address','Carrier Name','ISP','Device Model','WAN Type','WIFI SSID','Device Model' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Ookla Speedtest History'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table')
	
	db.close()
	return 
	
