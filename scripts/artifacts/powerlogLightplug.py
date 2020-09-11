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

def get_powerlogLightplug(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("10"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        DATETIME(LIGHTNINGCONNECTOR_TIMESTAMP + SYSTEM, 'UNIXEPOCH','LOCALTIME') AS ADJUSTED_TIMESTAMP,
        CASE IOACCESSORYPOWERMODE 
            WHEN "1" THEN "UNPLUGGED" 
            WHEN "3" THEN "PLUGGED IN" 
        END  AS "IO ACCESSORY POWER MODE",
        DATETIME(LIGHTNINGCONNECTOR_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_LIGHTNINGCONNECTOR_TIMESTAMP,
        DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
        SYSTEM AS TIME_OFFSET,
        LIGHTNINGCONNECTOR_ID AS "PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS TABLE ID" 
    	FROM
        (
        SELECT
            LIGHTNINGCONNECTOR_ID,
            LIGHTNINGCONNECTOR_TIMESTAMP,
            TIME_OFFSET_TIMESTAMP,
            MAX(TIME_OFFSET_ID) AS MAX_ID,
            IOACCESSORYPOWERMODE,
            SYSTEM
        FROM
            (
            SELECT
                PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS.TIMESTAMP AS LIGHTNINGCONNECTOR_TIMESTAMP,
                IOACCESSORYPOWERMODE,
                PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS.ID AS "LIGHTNINGCONNECTOR_ID" ,
                PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
                PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
                PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
            FROM
                PLBATTERYAGENT_EVENTFORWARD_LIGHTNINGCONNECTORSTATUS
            LEFT JOIN
                PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
            )
            AS LIGHTNINGCONNECTOR_STATE 
        GROUP BY
            LIGHTNINGCONNECTOR_ID 
        )
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

                report = ArtifactHtmlReport('Powerlog Lightning Connector Status')
                report.start_artifact_report(report_folder, 'Lightning Connector Status')
                report.add_script()
                data_headers = ('Adjusted Timestamp','Accesory Power Mode','Original Lightnint Connector Timestamp','Offset Timestamp','Table ID' )   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Lightning Connector'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog Lightning Connector'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Powerlog Lightning Connector Status')

        db.close()
        return      
    
    
