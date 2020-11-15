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

def get_interactionCcontacts(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("10"):
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(zinteractions.zstartdate + 978307200, 'unixepoch'),
        datetime(zinteractions.zenddate + 978307200, 'unixepoch'),
        zinteractions.zbundleid,
        zcontacts.zdisplayname,
        zcontacts.zidentifier,
        zinteractions.zdirection,
        zinteractions.zisresponse,
        zinteractions.zrecipientcount,
        datetime(zinteractions.zcreationdate + 978307200, 'unixepoch'),
        datetime(zcontacts.zcreationdate + 978307200, 'unixepoch'),
        zinteractions.zcontenturl
        from
        zinteractions 
        left join
        zcontacts 
        on zinteractions.zsender = zcontacts.z_pk        
        ''')
        
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        if version.parse(iOSversion) >= version.parse("10"):
            for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

            report = ArtifactHtmlReport('InteractionC')
            report.start_artifact_report(report_folder, 'Contacts')
            report.add_script()
            data_headers = ('Start Date','End Date','Bundle ID','Display Name','Identifier','Direction','Is Response','Recipient Count','Zinteractions Creation Date','Zcontacs Creation Date','Content URL')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'InteractionC Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'InteractonC Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in InteractionC Contacts')

    db.close()
    return      
    
    
    