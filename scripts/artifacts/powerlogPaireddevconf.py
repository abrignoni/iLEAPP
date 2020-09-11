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

def get_powerlogPaireddevconf(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("10"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
            BUILD,
            DEVICE,
            HWMODEL,
            PAIRINGID AS "PAIRING ID",
            ID AS "PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG TABLE ID" 
        FROM
            PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG
        ''')
    else:
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
            BUILD,
            DEVICE,
            ID AS "PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG TABLE ID" 
        FROM
            PLCONFIGAGENT_EVENTNONE_PAIREDDEVICECONFIG
        ''')
        
        
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        if version.parse(iOSversion) >= version.parse("10"):
            for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

            report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
            report.start_artifact_report(report_folder, 'Paired Device Configuration')
            report.add_script()
            data_headers = ('Timestamp','Build','Device','HW Model','Pairing ID','PairedDeviceConfig Table ID' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Paired Device Conf'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3]))
            
            report = ArtifactHtmlReport('Powerlog Paired Device Configuration')
            report.start_artifact_report(report_folder, 'Paired Device Configuration')
            report.add_script()
            data_headers = ('Timestamp','Build','Device','PairedDeviceConfig Table ID' )  
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Paired Device Conf'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Paired Device Configuration'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return      
    
    
