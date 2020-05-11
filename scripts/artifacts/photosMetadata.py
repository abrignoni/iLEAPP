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


def get_photosMetadata(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	#os.chmod(file_found, 0o0777)
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	Select
	z_pk,
	zfilename AS "File Name",
	zduration AS "Duration in Seconds",
	case
	when ztrashedstate = 1 then "Deleted"
	else "N/A"
	end AS "Is Deleted",
	case
	when zhidden =1 then "Hidden"
	else 'N/A'
	end AS "Is Hidden",
	datetime(ztrasheddate+978307200,'unixepoch','localtime') AS "Date Deleted",
	datetime(zaddeddate+978307200,'unixepoch','localtime') AS "Date Added",
	datetime(zdatecreated+978307200,'unixepoch','localtime') AS "Date Created",
	datetime(zmodificationdate+978307200,'unixepoch','localtime') AS "Date Modified",
	zdirectory AS "File Path"
	from zgenericasset
	""")

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
	
		description = ''
		report = ArtifactHtmlReport('Photos.sqlite')
		report.start_artifact_report(report_folder, 'Metadata', description)
		report.add_script()
		data_headers = ('Primary Key','Filename','Duration in Seconds','Is Deleted?','Is Hidden?','Date Deleted','Date Added','Date Created','Date Modified','File Path')     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Photos-sqlite Metadata'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available for Photos.sqlite metadata')
	
	db.close()
	return 
	