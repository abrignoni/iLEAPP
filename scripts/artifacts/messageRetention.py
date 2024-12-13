from datetime import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_messageRetention(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        if len(files_found) > 1:
            filetoprocessOne = seeker.search(f'*/mobile/Library/Preferences/com.apple.MobileSMS.plist')
            with open(filetoprocessOne[0], "rb") as fp:
                pl = plistlib.load(fp)
                indicator = 0
                
                for key, val in pl.items():
                    
                    if key == 'KeepMessageForDays':
                        if val == 0:
                            keep_val = 'Forever'
                        elif val == 365:
                            keep_val = '1 Year'
                        elif val == 30:
                            keep_val = '30 Days'
                        
                        data_list.append(('com.apple.MobileSMS.plist - Keep Messages for Days (iOS <=16)',val,file_found))
                        logdevinfo(f"<b>com.apple.MobileSMS.plist - Keep Messages for Days (iOS <=16): </b>{val}")
                        indicator = 1
                        
                    if key == 'SSKeepMessages':
                        if val == 0:
                            keep_val = 'Forever'
                        elif val == 365:
                            keep_val = '1 Year'
                        elif val == 30:
                            keep_val = '30 Days'
                        
                        data_list.append(('com.apple.MobileSMS.plist - Keep Messages for Days (iOS 17+)',val,file_found))
                        logdevinfo(f"<b>com.apple.MobileSMS.plist - Keep Messages for Days (iOS 17+): </b>{val}")
                        indicator = 1
                        
                if indicator == 0:
                    data_list.append(('com.apple.MobileSMS.plist - Keep Messages for Days','No value',filetoprocessOne[0]))
                    logdevinfo(f"<b>com.apple.MobileSMS.plist - Keep Messages for Days: </b>No Value")
            
            filetoprocessTwo = seeker.search(f'*/mobile/Library/Preferences/com.apple.mobileSMS.plist')
            with open(filetoprocessTwo[0], "rb") as fp:
                pl = plistlib.load(fp)
                indicator = 0
                
                for key, val in pl.items():
                    if key == 'KeepMessageForDays':
                        if val == 0:
                            keep_val = 'Forever'
                        elif val == 365:
                            keep_val = '1 Year'
                        elif val == 30:
                            keep_val = '30 Days'                            
                        
                        data_list.append(('com.apple.mobileSMS.plist - Keep Messages for Days (iOS <=16)',keep_val,file_found))
                        logdevinfo(f"<b>com.apple.mobileSMS.plist - Keep Messages for Days (iOS <=16): </b>{keep_val}")
                        indicator = 1
                        
                    if key == 'SSKeepMessages':
                        if val == 0:
                            keep_val = 'Forever'
                        elif val == 365:
                            keep_val = '1 Year'
                        elif val == 30:
                            keep_val = '30 Days'
                            
                        data_list.append(('com.apple.mobileSMS.plist - Keep Messages for Days (iOS 17+)',keep_val,file_found))
                        logdevinfo(f"<b>com.apple.mobileSMS.plist - Keep Messages for Days (iOS 17+): </b>{keep_val}")
                        indicator = 1
                        
                if indicator == 0:
                    data_list.append(('com.apple.mobileSMS.plist - Keep Messages for Days','No value',filetoprocessTwo[0]))
                    logdevinfo(f"<b>com.apple.mobileSMS.plist - Keep Messages for Days: </b>No Value")
            break
        
        else:
            with open(file_found, "rb") as fp:
                base_file = os.path.basename(file_found)                
                pl = plistlib.load(fp)
                indicator = 0
            
                for key, val in pl.items():
                    if key == 'KeepMessageForDays':
                        if val == 0:
                            keep_val = 'Forever'
                        elif val == 365:
                            keep_val = '1 Year'
                        elif val == 30:
                            keep_val = '30 Days'
                            
                        data_list.append((f"{base_file} - Keep Messages for Days (iOS <=16)",keep_val,file_found))
                        logdevinfo(f"<b>{base_file} - Keep Messages for Days (iOS <=16): </b>{keep_val}")
                        indicator = 1
                        
                    if key == 'SSKeepMessages':
                        if val == 0:
                            keep_val = 'Forever'
                        elif val == 365:
                            keep_val = '1 Year'
                        elif val == 30:
                            keep_val = '30 Days'
                            
                        data_list.append((f"{base_file} - Keep Messages for Days (iOS 17+)",keep_val,file_found))
                        logdevinfo(f"<b>{base_file} - Keep Messages for Days (iOS 17+): </b>{keep_val}")
                        indicator = 1
                    
                if indicator == 0:
                    data_list.append((f"{base_file} - Keep Messages for Days",'No value',file_found))
                    logdevinfo(f"<b>{base_file} - Keep Message for Days: </b>No Value")
            
    if len(data_list) > 0:
        report = ArtifactHtmlReport('iOS Message Retention')
        report.start_artifact_report(report_folder, 'iOS Message Retention')
        report.add_script()
        data_headers = ('Key','Value(s)','Path')
        report.write_artifact_data_table(data_headers, data_list, 'File path in the report below')
        report.end_artifact_report()
        
        tsvname = 'iOS Message Retention'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No iOS Message Retention data')
            
__artifacts__ = {
    "messageRetention": (
        "Identifiers",
        ('*/com.apple.MobileSMS.plist','*/com.apple.mobileSMS.plist'),
        get_messageRetention)
}