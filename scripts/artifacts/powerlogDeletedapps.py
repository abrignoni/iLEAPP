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

def get_powerlogDeletedapps(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("11"):
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
                DATETIME(APPDELETEDDATE, 'UNIXEPOCH') AS "APP DELETED DATE",
                DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
                APPNAME AS "APP NAME",
                APPEXECUTABLE AS "APP EXECUTABLE NAME",
                APPBUNDLEID AS "BUNDLE ID",
                APPBUILDVERSION AS "APP BUILD VERSION",
                APPBUNDLEVERSION AS "APP BUNDLE VERSION",
                APPTYPE AS "APP TYPE",
                ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
            FROM
                PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
            WHERE
                APPDELETEDDATE > 0

        """)
    elif version.parse(iOSversion) == version.parse("10"):
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
                DATETIME(APPDELETEDDATE, 'UNIXEPOCH') AS "APP DELETED DATE",
                DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
                APPNAME AS "APP NAME",
                APPEXECUTABLE AS "APP EXECUTABLE NAME",
                APPBUNDLEID AS "BUNDLE ID",
                APPBUILDVERSION AS "APP BUILD VERSION",
                APPBUNDLEVERSION AS "APP BUNDLE VERSION",
                --APPTYPE AS "APP TYPE",
                ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
            FROM
                PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
            WHERE
                APPDELETEDDATE > 0
        """)
    elif version.parse(iOSversion) == version.parse("9"):
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
                DATETIME(APPDELETEDDATE, 'UNIXEPOCH') AS "APP DELETED DATE",
                DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
                APPNAME AS "APP NAME",
                APPBUNDLEID AS "BUNDLE ID",
                ID AS "PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS TABLE ID" 
            FROM
                PLAPPLICATIONAGENT_EVENTNONE_ALLAPPS 
            WHERE
                APPDELETEDDATE > 0
        """)
    else:
        logfunc("Unsupported version for Powerlog Deleted Apps iOS version: " + iOSversion)
        return ()
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        if version.parse(iOSversion) >= version.parse("11"):	
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report = ArtifactHtmlReport('Powerlog Deleted Apps')
            report.start_artifact_report(report_folder, 'Deleted Apps')
            report.add_script()
            data_headers = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type','Table ID')  
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Deleted Apps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Deleted Apps'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        elif version.parse(iOSversion) == version.parse("10"):
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
                    
            report = ArtifactHtmlReport('Powerlog Deleted Apps')
            report.start_artifact_report(report_folder, 'Deleted Apps')
            report.add_script()
            data_headers = ('App Deleted Date','Timestamp','App Name','App Executable Name','Bundle ID','App Build Version','App Bundle Version','App Type','Table ID')             
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Deleted Apps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Deleted Apps'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        elif version.parse(iOSversion) == version.parse("9"):
            for row in all_rows:    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
                    
            report = ArtifactHtmlReport('Powerlog Deleted Apps')
            report.start_artifact_report(report_folder, 'Deleted Apps')
            report.add_script()
            data_headers = ('App Deleted Date','Timestamp','App Name','Bundle ID','Table ID') 
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Powerlog Deleted Apps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Powerlog Deleted Apps'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Powerlog Delete Apps')
    
