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


def get_calendarAll(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	db = open_sqlite_db_readonly(file_found)
	cursor = db.cursor()
	cursor.execute(
	"""
	select 
	title,
	flags,
	color,
	symbolic_color_name,
	external_id,
	self_identity_email
	from Calendar
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))
	
		description = ''
		report = ArtifactHtmlReport('Calendar List')
		report.start_artifact_report(report_folder, 'List', description)
		report.add_script()
		data_headers = ('Title','Flags','Color','Symbolic Color Name','External ID','Self Identity Email')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Calendar List '
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available for Calendar List')
	
	cursor.execute(
	"""
	Select
	DATETIME(start_date + 978307200, 'UNIXEPOCH') as startdate,
	start_tz,
	DATETIME(end_date + 978307200, 'UNIXEPOCH') as enddate,
	end_tz,
	all_day,
	summary,
	calendar_id,
	DATETIME(last_modified+ 978307200, 'UNIXEPOCH') as lastmod
	from CalendarItem
	order by startdate
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
	
		description = ''
		report = ArtifactHtmlReport('Calendar Items')
		report.start_artifact_report(report_folder, 'Items', description)
		report.add_script()
		data_headers = ('Start Date','Start Timezone','End Date','End Timezone','All Day?','Summary','Calendar ID','Last Modified')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Calendar Items'
		tsv(report_folder, data_headers, data_list, tsvname)
		
		tlactivity = 'Calendar Items'
		timeline(report_folder, tlactivity, data_list, data_headers)
	else:
		logfunc('No data available for Calendar Items')
	
	cursor.execute(
	"""
	SELECT
	display_name,
	address,
	first_name,
	last_name
	from Identity
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3]))
	
		description = ''
		report = ArtifactHtmlReport('Calendar Identity')
		report.start_artifact_report(report_folder, 'Identity', description)
		report.add_script()
		data_headers = ('Display Name','Address','First Name','Last Name')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Calendar Identity'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available for Calendar Identity')