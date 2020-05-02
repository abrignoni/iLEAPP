import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows 

    
def get_knowCusage(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor = db.cursor()

    cursor.execute(
        """
	SELECT
	datetime(ZOBJECT.ZCREATIONDATE+978307200,'UNIXEPOCH') as "ENTRY CREATION", 
	CASE ZOBJECT.ZSTARTDAYOFWEEK 
		WHEN "1" THEN "Sunday"
		WHEN "2" THEN "Monday"
		WHEN "3" THEN "Tuesday"
		WHEN "4" THEN "Wednesday"
		WHEN "5" THEN "Thursday"
		WHEN "6" THEN "Friday"
		WHEN "7" THEN "Saturday"
	END "DAY OF WEEK",
	ZOBJECT.ZSECONDSFROMGMT/3600 AS "GMT OFFSET",
	datetime(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') as "START", 
	datetime(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') as "END", 
	(ZOBJECT.ZENDDATE-ZOBJECT.ZSTARTDATE) as "USAGE IN SECONDS",
	ZOBJECT.ZSTREAMNAME, 
	ZOBJECT.ZVALUESTRING
	FROM ZOBJECT
	WHERE ZSTREAMNAME IS "/app/inFocus" 
	ORDER BY "START"	"""
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []    
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    description = ''
    report = ArtifactHtmlReport('KnowledgeC App Usage')
    report.start_artifact_report(report_folder, 'KnowledgeC App Usage', description)
    report.add_script()
    data_headers = ('Entry Creation','Day of the Week','GMT Offset','Start','End','Usage in Seconds','ZSTREAMNAME', 'ZVALUESTRING' )     
    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
    report.end_artifact_report()
