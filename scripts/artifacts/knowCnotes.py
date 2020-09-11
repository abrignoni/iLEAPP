import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_knowCnotes(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        DATETIME(ZOBJECT.ZSTARTDATE+978307200,'UNIXEPOCH') AS "START", 
        DATETIME(ZOBJECT.ZENDDATE+978307200,'UNIXEPOCH') AS "END",
        ZOBJECT.ZVALUESTRING AS "BUNDLE ID",
        ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ACTIVITYTYPE AS "ACTIVITY TYPE", 
        ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__USERACTIVITYREQUIREDSTRING AS "USER ACTIVITY REQUIRED STRING",
        ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMIDENTIFIER AS "ID",
        ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__ITEMRELATEDUNIQUEIDENTIFIER AS "UNIQUE ID",
        ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__USERACTIVITYUUID AS "ACTIVITY UUID",
        ZSOURCE.ZSOURCEID AS "SOURCE ID",
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
        DATETIME(ZOBJECT.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "ENTRY CREATION",
        DATETIME(ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONACTIVITYMETADATAKEY__EXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "EXPIRATION DATE",
        ZOBJECT.ZUUID AS "UUID", 
        ZOBJECT.Z_PK AS "ZOBJECT TABLE ID" 
    FROM
        ZOBJECT 
        LEFT JOIN
            ZSTRUCTUREDMETADATA 
            ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
        LEFT JOIN
            ZSOURCE 
            ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
    WHERE
        ZSTREAMNAME IS "/app/activity"
        AND ("BUNDLE ID" = "com.apple.mobilenotes" OR "BUNDLE ID" = "com.apple.Notes")
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

        report = ArtifactHtmlReport('KnowledgeC Notes - Activity')
        report.start_artifact_report(report_folder, 'Notes - Activity')
        report.add_script()
        data_headers = ('Start','End','Bundle ID','Activity Type','User Activity Required String','ID','Unique ID','Activity UUID','Source ID','Day of Week','GMT Offset','Entry Creation','Expiration Date', 'UUID','ZOBJECT Table ID' )   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'KnowledgeC Notes Activity'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'KnowledgeC Notes Activity'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return      
    
    
