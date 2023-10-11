import datetime
import os

from scripts.builds_ids import OS_build
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_restoreLog(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    pattern = 'data = '
    pattern1 = '\"originalOSVersion\":\"'
    pattern2 = '\"currentOSVersion\":\"'
    pattern3 = '\"deviceModel\":\"'
    pattern4 = '\"eventTime\":\"'
    pattern5 = '\"batteryIsCharging\":'
    pattern6 = '\"deviceClass\":\"'
    pattern7 = '\"event\":\"'
    og_version_num = ''
    cur_version_num = ''
    originalOSBuild = ''
    currentOSBuild = ''

    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, "r", encoding="utf-8") as f:
            data = f.readlines()
            for line in data:
                if pattern in line:
                    
                    if pattern1 in line:
                    
                        if pattern1 in line:
                            splitline1 = line.partition(pattern1)[2]
                            originalOSBuild = splitline1[:splitline1.find("\"")]
                            
                            for key, value in OS_build.items():
                                if originalOSBuild == key:
                                    og_version_num = value
                                    break
                                else: og_version_num = "Unknown"
                        else: pass
                        
                        if pattern2 in line:
                            splitline2 = line.partition(pattern2)[2]
                            currentOSBuild = splitline2[:splitline2.find("\"")]
                            
                            for key, value in OS_build.items():
                                if currentOSBuild == key:
                                    cur_version_num = value
                                    break
                                else: cur_version_num = "Unknown"
                        
                        if pattern3 in line:
                            splitline3 = line.partition(pattern3)[2]
                            deviceModel = splitline3[:splitline3.find("\"")]
                        else: pass
                        
                        if pattern4 in line:
                            splitline4 = line.partition(pattern4)[2]
                            eventTime = splitline4[:splitline4.find("\"")]
                            timestamp_formatted = datetime.datetime.fromtimestamp(int(eventTime)/1000).strftime('%Y-%m-%d %H:%M:%S')
                        else: pass
                        
                        if pattern5 in line:
                            splitline5 = line.partition(pattern5)[2]
                            batteryIsCharging = splitline5[:splitline5.find(",")]
                        else: pass
                        
                        if pattern6 in line:
                            splitline6 = line.partition(pattern6)[2]
                            deviceClass = splitline6[:splitline6.find("\"")]
                        else: pass
                        
                        if pattern7 in line:
                            splitline7 = line.partition(pattern7)[2]
                            event = splitline7[:splitline7.find("\"")]
                        else: pass
                        
                        data_list.append((timestamp_formatted,originalOSBuild,og_version_num,currentOSBuild,cur_version_num,event,deviceClass,deviceModel,batteryIsCharging))
                        
                    else: pass
                    
            
    num_entries = len(data_list)
    if num_entries > 0:
        report = ArtifactHtmlReport('Mobile Software Update - Restore Log')
        report.start_artifact_report(report_folder, 'Mobile Software Update - Restore Log')
        report.add_script()
        data_headers = ('Timestamp','Original OS Build','Original OS Version','Current OS Build','Current OS Version','Event','Device','Model','Battery Is Charging')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Mobile Software Update - Restore Log'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Mobile Software Update - Restore Log'
        timeline(report_folder, tlactivity, data_list, data_headers)           
        
    else:
        logfunc('No Mobile Software Update - Restore Log data available')

__artifacts__ = {
    "restoreLog": (
        "Mobile Software Update",
        ('*/mobile/MobileSoftwareUpdate/restore.log'),
        get_restoreLog)
}
