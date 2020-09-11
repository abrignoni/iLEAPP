import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows  
from scripts.ccl import ccl_bplist

def get_powerlogTimezone(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
     SELECT
    DATETIME(TIMEZONE_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
    TIMEZONENAME AS "TIME ZONE NAME",
    COUNTRYCODE AS "COUNTRY CODE",
    LOCALEID AS "LOCALE ID",
    SECONDSFROMGMT / 3600 AS "SECONDS FROM GMT",
    TIMEZONEISINDST AS "TIME ZONE IN DST",
    TRIGGER AS "TRIGGER",
    DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
    SYSTEM AS TIME_OFFSET,
    TIMEZONE_ID AS "PLLOCALEAGENT_EVENTFORWARD_TIMEZONE TABLE ID" 
	FROM
    (
    SELECT
        TIMEZONE_ID,
        TIMEZONE_TIMESTAMP,
        TIME_OFFSET_TIMESTAMP,
        MAX(TIME_OFFSET_ID) AS MAX_ID,
        TIMEZONENAME,
        COUNTRYCODE,
        LOCALEID,
        SECONDSFROMGMT,
        TIMEZONEISINDST,
        TRIGGER,
        SYSTEM
    FROM
        (
        SELECT
            PLLOCALEAGENT_EVENTFORWARD_TIMEZONE.TIMESTAMP AS TIMEZONE_TIMESTAMP,
            TIMEZONENAME,
            COUNTRYCODE,
            LOCALEID,
            SECONDSFROMGMT,
            TIMEZONEISINDST,
            TRIGGER,
            PLLOCALEAGENT_EVENTFORWARD_TIMEZONE.ID AS "TIMEZONE_ID" ,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
        FROM
            PLLOCALEAGENT_EVENTFORWARD_TIMEZONE
        LEFT JOIN
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
        )
        AS TIMEZONE_STATE 
    GROUP BY
        TIMEZONE_ID 
    )
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

        report = ArtifactHtmlReport('Powerlog Timezones')
        report.start_artifact_report(report_folder, 'Timezones')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Timezone Name','Country Code','Locale ID','Seconds from GMT','Timezone in DTS','Trigger','Offset Timestamp','Time Offset','Timezon Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Timezones'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Timezones'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   