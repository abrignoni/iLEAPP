import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_restoreLog(files_found, report_folder, seeker, wrap_text):

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
    
    OS_dict = {
    "15A372":"iOS 11.0",
    "15A402":"iOS 11.0.1",
    "15A403":"iOS 11.0.1",
    "15A8391":"iOS 11.0.1",
    "15A421":"iOS 11.0.2",
    "15A432":"iOS 11.0.3",
    "15B93":"iOS 11.1",
    "15B101":"iOS 11.1",
    "15B150":"iOS 11.1.1",
    "15B202":"iOS 11.1.2",
    "15C114":"iOS 11.2",
    "15C153":"iOS 11.2.1",
    "15C202":"iOS 11.2.2",
    "15D60":"iOS 11.2.5",
    "15D100":"iOS 11.2.6",
    "15E216":"iOS 11.3",
    "15E218":"iOS 11.3",
    "15E302":"iOS 11.3.1",
    "15F79":"iOS 11.4",
    "15G77":"iOS 11.4.1",
    "16A366":"iOS 12.0",
    "16A404":"iOS 12.0.1",
    "16A405":"iOS 12.0.1",
    "16B92":"iOS 12.1",
    "16B93":"iOS 12.1",
    "16B94":"iOS 12.1",
    "16C50":"iOS 12.1.1",
    "16C104":"iOS 12.1.2",
    "16D39":"iOS 12.1.3",
    "16D40":"iOS 12.1.3",
    "16D57":"iOS 12.1.4",
    "16E227":"iOS 12.2",
    "16F156":"iOS 12.3",
    "16F203":"iOS 12.3.1",
    "16F8202":"iOS 12.3.1",
    "16F250":"iOS 12.3.2",
    "16G77":"iOS 12.4",
    "16G102":"iOS 12.4.1",
    "16G114":"iOS 12.4.2",
    "16G130":"iOS 12.4.3",
    "16G140":"iOS 12.4.4",
    "16G161":"iOS 12.4.5",
    "16G183":"iOS 12.4.6",
    "16G192":"iOS 12.4.7",
    "16G201":"iOS 12.4.8",
    "16H5":"iOS 12.4.9",
    "16H20":"iOS 12.5",
    "16H22":"iOS 12.5.1",
    "16H30":"iOS 12.5.2",
    "16H41":"iOS 12.5.3",
    "16H50":"iOS 12.5.4",
    "16H62":"iOS 12.5.5",   
    "17A577":"iOS 13.0",
    "17A844":"iOS 13.1",
    "17A854":"iOS 13.1.1",
    "17A860":"iOS 13.1.2",
    "17A861":"iOS 13.1.2",
    "17A878":"iOS 13.1.3",
    "17B84":"iOS 13.2",
    "17B90":"iOS 13.2.1",
    "17B102":"iOS 13.2.2",
    "17B111":"iOS 13.2.3",
    "17C54":"iOS 13.3",
    "17D50":"iOS 13.3.1",
    "17E255":"iOS 13.4",
    "17E8255":"iOS 13.4",
    "17E262":"iOS 13.4.1",
    "17E8258":"iOS 13.4.1",
    "17F75":"iOS 13.5",
    "17F80":"iOS 13.5.1",
    "17G68":"iOS 13.6",
    "17G80":"iOS 13.6.1",
    "17H35":"iOS 13.7",
    "18A373":"iOS 14.0",
    "18A393":"iOS 14.0.1",
    "18A8395":"iOS 14.1",
    "18B92":"iOS 14.2",
    "18B111":"iOS 14.2",
    "18B121":"iOS 14.2.1",
    "18C66":"iOS 14.3",
    "18D52":"iOS 14.4",
    "18D61":"iOS 14.4.1",
    "18D70":"iOS 14.4.2",
    "18E199":"iOS 14.5",
    "18E212":"iOS 14.5.1",
    "18F72":"iOS 14.6",
    "18G69":"iOS 14.7",
    "18G82":"iOS 14.7.1",
    "18H17":"iOS 14.8",
    "18H107":"iOS 14.8.1",
    "19A346":"iOS 15.0",
    "19A348":"iOS 15.0.1",
    "19A404":"iOS 15.0.2",
    "19B74":"iOS 15.1",
    "19B81":"iOS 15.1.1",
    "19C56":"iOS 15.2",
    "19C57":"iOS 15.2",
    "19C63":"iOS 15.2.1",
    "19D50":"iOS 15.3",
    "19D52":"iOS 15.3.1",
    "19E241":"iOS 15.4",
    "19E258":"iOS 15.4.1",
    "19F77":"iOS 15.5",
    "19G71":"iOS 15.6",
    "19G82":"iOS 15.6.1",
    "19H12":"iOS 15.7",
    "20A362":"iOS 16.0",
    "20A371":"iOS 16.0.1",
    "20A380":"iOS 16.0.2",
    "20A392":"iOS 16.0.3",
    "20B82":"iOS 16.1",
    }

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
                            
                            for key, value in OS_dict.items():
                                if originalOSBuild == key:
                                    og_version_num = value
                                    break
                                else: og_version_num = "Unknown"
                        else: pass
                        
                        if pattern2 in line:
                            splitline2 = line.partition(pattern2)[2]
                            currentOSBuild = splitline2[:splitline2.find("\"")]
                            
                            for key, value in OS_dict.items():
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
        ('**/private/var/mobile/MobileSoftwareUpdate/restore.log'),
        get_restoreLog)
}
