import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_interactionCcontacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
    
    db = open_sqlite_db_readonly(file_found)
    
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
            for row in all_rows:
                starttime = convert_ts_human_to_utc(row[0])
                starttime = convert_utc_human_to_timezone(starttime,timezone_offset)
                
                endtime = convert_ts_human_to_utc(row[1])
                endtime = convert_utc_human_to_timezone(endtime,timezone_offset)
                
                zinteractcreated = convert_ts_human_to_utc(row[8])
                zinteractcreated = convert_utc_human_to_timezone(zinteractcreated,timezone_offset)
                
                zcontactscreated = row[9]
                if zcontactscreated is None:
                    zcontactscreated = ''
                    
                else:
                    zcontactscreated = convert_ts_human_to_utc(zcontactscreated)
                    zcontactscreated = convert_utc_human_to_timezone(zcontactscreated,timezone_offset)
                
                data_list.append((starttime,endtime,row[2],row[3],row[4],row[5],row[6],row[7],zinteractcreated,zcontactscreated,row[10]))
            
            report = ArtifactHtmlReport('InteractionC')
            report.start_artifact_report(report_folder, 'Contacts')
            report.add_script()
            data_headers = ('Start Date','End Date','Bundle ID','Display Name','Identifier','Direction','Is Response','Recipient Count','Zinteractions Creation Date','Zcontacts Creation Date','Content URL')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'InteractionC Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'InteractionC Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in InteractionC Contacts')
        
    if version.parse(iOSversion) >= version.parse("10"):
        cursor = db.cursor()
        cursor.execute('''
        select
            datetime(zinteractions.ZCREATIONDATE + 978307200, 'unixepoch'),
            ZINTERACTIONS.zbundleid,
            ZINTERACTIONS.ztargetbundleid,
            ZINTERACTIONS.zuuid,
            ZATTACHMENT.zcontenttext,
            ZATTACHMENT.zuti,
            ZATTACHMENT.zcontenturl
            from zinteractions
            inner join z_1interactions
            on zinteractions.z_pk = z_1interactions.z_3interactions
            inner join zattachment on z_1interactions.z_1attachments = zattachment.z_pk
        ''')
        
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        if version.parse(iOSversion) >= version.parse("10"):
            for row in all_rows:
                creationdate = convert_ts_human_to_utc(row[0])
                creationdate = convert_utc_human_to_timezone(creationdate,timezone_offset)
                
                data_list.append((creationdate,row[1],row[2],row[3],row[4],row[5],row[6]))
                
            report = ArtifactHtmlReport('InteractionC')
            report.start_artifact_report(report_folder, 'Attachments')
            report.add_script()
            data_headers = ('Creation Date', 'Bundle ID', 'Target Bundle ID', 'ZUUID', 'Content Text', 'Uniform Type ID', 'Content URL')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'InteractionC Attachments'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'InteractionC Attachments'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in InteractionC Attachments')
    

    db.close()
    return      
    
__artifacts__ = {
    "interactionCcontacts": (
        "InteractionC",
        ('**/interactionC.db*'),
        get_interactionCcontacts)
}
