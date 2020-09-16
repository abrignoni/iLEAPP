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

def get_powerlogAirdrop(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
                DATETIME(AIRDROP_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
                STATE,
                SUBEVENT,
                BUNDLEID AS BUNDLE_ID,
                PID,
                DATETIME(AIRDROP_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_AIRDROP_TIMESTAMP,
                DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
                SYSTEM AS TIME_OFFSET,
                AIRDROP_ID AS "PLXPCAGENT_EVENTFORWARD_AIRDROP TABLE ID"
            FROM
                (
                SELECT
                    BUNDLEID,
                    AIRDROP_ID,
                    AIRDROP_TIMESTAMP,
                    TIME_OFFSET_TIMESTAMP,
                    MAX(TIME_OFFSET_ID) AS MAX_ID,
                    SYSTEM,
                    PID,
                    SUBEVENT,
                    STATE
                FROM
                    (
                SELECT
                    PLXPCAGENT_EVENTFORWARD_AIRDROP.TIMESTAMP AS AIRDROP_TIMESTAMP,
                    PLXPCAGENT_EVENTFORWARD_AIRDROP.BUNDLEID,
                    PLXPCAGENT_EVENTFORWARD_AIRDROP.PID,
                    PLXPCAGENT_EVENTFORWARD_AIRDROP.SUBEVENT,
                    PLXPCAGENT_EVENTFORWARD_AIRDROP.STATE,
                    PLXPCAGENT_EVENTFORWARD_AIRDROP.ID AS "AIRDROP_ID",
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM,
                    BUNDLEID 
                FROM
                    PLXPCAGENT_EVENTFORWARD_AIRDROP 
                LEFT JOIN
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
                    )
                AS AIRDROPSTATE 
                GROUP BY
                    AIRDROP_ID 
                )
        ''')
        
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report = ArtifactHtmlReport('Powerlog Airdrop Connections Info')
                report.start_artifact_report(report_folder, 'Airdrop Connections Info')
                report.add_script()
                data_headers = ('Adjusted Timestamp','State','Subevent','Bundle ID','PID','Original Airdrop Timestamp','Offset Timestamp','Time Offset', 'Airdrop Table ID' )   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Airdrop Connections Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'KnowledgeC Airdrop Connections Info'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Airdop Connection Info')

        db.close()
        return      
    
    
