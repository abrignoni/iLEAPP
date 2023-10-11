from datetime import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.utcfromtimestamp(unix_timestamp)
    return(finaltime)

def get_backupSettings(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'LastiTunesBackupDate':
                lastime = timestampsconv(val)
                data_list.append(('Last iTunes Backup Date', lastime))
                logdevinfo(f"Last iTunes Backup Date: {lastime}")
            elif key == 'LastiTunesBackupTZ':
                data_list.append((key, val))
                logdevinfo(f"Last iTunes Backup TZ: {val}")
            elif key == 'LastCloudBackupDate':
                lastcloudtime = timestampsconv(val)
                data_list.append(('Last Cloud iTunes Backup Date', lastcloudtime))
                logdevinfo(f"Last Cloud iTunes Backup Date: {lastcloudtime}")
            elif key == 'LastCloudBackupTZ':
                data_list.append((key, val))
                logdevinfo(f"Last Cloud iTunes Backup TZ: {val}")
            elif key == 'CloudBackupEnabled':
                data_list.append((key,val))
                logdevinfo(f"Cloud Backup Enabled: {val}")
            else:
                data_list.append((key, val ))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('iPhone Backup Settings')
        report.start_artifact_report(report_folder, 'iPhone Backup Settings')
        report.add_script()
        data_headers = ('Key','Values' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'iPhone Backup Settings'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Find iPhone Backup Settings')
            

__artifacts__ = {
    "backupSettings": (
        "Identifiers",
        ('*/mobile/Library/Preferences/com.apple.mobile.ldbackup.plist'),
        get_backupSettings)
}
