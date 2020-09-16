import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogLocuseapp(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(LOCATIONAGENT_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
            DATETIME(TIMESTAMPLOGGED+ SYSTEM, 'UNIXEPOCH') AS "TIMESTAMP LOGGED (ADJ)",
            DATETIME(TIMESTAMPEND + SYSTEM, 'UNIXEPOCH') AS "TIMESTAMP END (ADJ)",
            BUNDLEID AS "BUNDLE ID",
            TYPE AS "TYPE",
            LOCATIONDESIREDACCURACY AS "LOCATION DESIRED ACCURACY",
            LOCATIONDISTANCEFILTER AS "LOCATION DISTANCE FILTER",
            CLIENT AS "CLIENT",
            EXECUTABLE AS "EXECUTABLE",
            DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
            SYSTEM AS TIME_OFFSET,
            LOCATIONAGENT_ID AS "PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS TABLE ID" 
        	FROM
            (
            SELECT
                LOCATIONAGENT_ID,
                LOCATIONAGENT_TIMESTAMP,
                TIME_OFFSET_TIMESTAMP,
                MAX(TIME_OFFSET_ID) AS MAX_ID,
                TIMESTAMPEND,
                TIMESTAMPLOGGED,
                BUNDLEID,
                TYPE,
                LOCATIONDESIREDACCURACY,
                LOCATIONDISTANCEFILTER,
                CLIENT,
                EXECUTABLE,
                SYSTEM
            FROM
                (
                SELECT
                    PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS.TIMESTAMP AS LOCATIONAGENT_TIMESTAMP,
                    TIMESTAMPEND,
                    TIMESTAMPLOGGED,
                    BUNDLEID,
                    TYPE,
                    LOCATIONDESIREDACCURACY,
                    LOCATIONDISTANCEFILTER,
                    CLIENT,
                    EXECUTABLE,
                    PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS.ID AS "LOCATIONAGENT_ID" ,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
                FROM
                    PLLOCATIONAGENT_EVENTFORWARD_CLIENTSTATUS
                LEFT JOIN
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
                )
                AS LOCATIONAGENT_STATE 
            GROUP BY
                LOCATIONAGENT_ID 
            )        
        ''')
        
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

                report = ArtifactHtmlReport('Powerlog Location Use by App')
                report.start_artifact_report(report_folder, 'Location Use by App')
                report.add_script()
                data_headers = ('Adjusted Timestamp','Timestamp Logged','Timestamp End','Bundle ID','Type','Location Desired Accuracy','Location Distance Filter','Client','Executable','Offset Timestamp','Time Offset', 'Client Status Table ID' )   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Location Use by App'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog Location Use by App'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Location Use by App')

        db.close()
        return      
    
    
