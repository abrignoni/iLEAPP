""""
Developed by Evangelos D. (@theAtropos4n6)

Research for this artifact was conducted by Evangelos Dragonas, Costas Lambrinoudakis and Michael Kotsis. 
For more information read their research paper here: Link_to_be_uploaded

Updated:27-03-2023

Hikvision is a well-known app that is used to remotely access/operate CCTV systems. Currently the following information can be interpreted:

-Hikvision - CCTV Channels: retrieves info for the available CCTV record channels 
-Hikvision - CCTV Info: Information about the CCTV system
-Hikvision - CCTV Activity: User Interaction with the app. Unfortunately it is not easy to attribute user actions but indirectly can indicate remote live view/play back from CCTV footage.
-Hikvision - User Created Media: The media files the user created while viewing footage from the CCTV

"""
import sqlite3
import os
import textwrap
import scripts.artifacts.artGlobals


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly,media_to_html

def get_hikvision(files_found, report_folder, seeker, wrap_text, timezone_offset):
    separator_1 = '/'
    separator_2 = "\\"
    media_data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if file_name == 'database.hik':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #CCTV Available Channels
            cursor.execute('''
                select 
                nDeviceID,
                nChannelNo,
                chChannelName,
                case  nEnable
                    when '0' then 'Disabled'
                    when '1' then 'Enabled'
                end
                from ChannelInfo 
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Hikvision - CCTV Channels')
                report.start_artifact_report(report_folder, 'Hikvision - CCTV Channels')
                report.add_script()
                data_headers = ('Device ID','Channel No.','Channel Name','Status') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Hikvision - CCTV Channels'
                tsv(report_folder, data_headers, data_list, tsvname)
            
            else:
                logfunc(f'No Hikvision - CCTV Channels data available')
            
            #CCTV Info
            cursor.execute('''
                select 
                    nDeviceID,
                    chDeviceName,
                    chDeviceSerialNo,
                    nDevicePort,
                    nChannelNum,
                    chDDNSAddr,
                    nDDNSPort
                from DeviceInfo
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Hikvision - CCTV Info')
                report.start_artifact_report(report_folder, 'Hikvision - CCTV Info')
                report.add_script()
                data_headers = ('ID','Name/IP','Serial Number','Port','Channels','DDNS Address','DDNS Port') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Hikvision - CCTV Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Hikvision - CCTV Info data available')

            db.close()

        if file_name == 'YSDCLogItem.sqlite':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #CCTV Activity
            cursor.execute('''
            SELECT
            datetime(time/1000,'unixepoch'),
            datetime(time/1000,'unixepoch','localtime'),
            systemName as 'Record Type',
            data
            FROM YSDCLogItem
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Hikvision - CCTV Activity')
                report.start_artifact_report(report_folder, 'Hikvision - CCTV Activity')
                report.add_script()
                data_headers = ('Timestamp (UTC)','Timestamp (Local)','Record Type','Activity') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Hikvision - CCTV Activity'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Hikvision - CCTV Activity'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Hikvision - CCTV Activity data available')

        #CCTV - User Created Media - Collecting Files
        if file_name.endswith(".jpg") or file_name.endswith(".mov") or file_name.endswith(".mp4"):
            #The files found grep input returns many files are not part of the app (false positives). This block of code ensures that each media file collected is part of the app's data
            if separator_1 in file_found:
                media_file_path = file_found.split(separator_1)
            else:
                media_file_path = file_found.split(separator_2)

            if len(media_file_path) > 5:
                doc_in_path = "True" if media_file_path[-5] == "Documents" else "False"
                year_in_path = "True" if media_file_path[-4].isdigit() and len(media_file_path[-4]) == 4 else "False"
                month_in_path = "True" if media_file_path[-3].isdigit() and len(media_file_path[-3]) == 2 else "False"
                day_in_path = "True" if media_file_path[-2].isdigit() and len(media_file_path[-2]) == 2 else "False"
                path_flags = [doc_in_path,year_in_path,month_in_path,day_in_path]

                if "False" not in path_flags:
                    temp_tuple = ()
                    temp_tuple = (file_found,file_name,file_name)
                    media_data_list.append(temp_tuple)
            
    #CCTV - User Created Media - Reporting Files
    media_files =  len(media_data_list)
    if media_files > 0:
        report = ArtifactHtmlReport('Hikvision - User Created Media')
        report.start_artifact_report(report_folder, 'Hikvision - User Created Media')
        report.add_script()
        data_headers = ('File Path','File Name', 'File Content') 
        data_list = []
        for mfile in media_data_list:          
            if mfile[2] is not None:
                media = media_to_html(mfile[2], files_found, report_folder)
            data_list.append((mfile[0],mfile[1],media))
        media_files_dir = "/private/var/mobile/Containers/Data/Application/[Application-GUID]/Documents/YYYY/MM/DD" #Generic path of the media files. Each file is stored within seperate dirs based on its creation date
        report.write_artifact_data_table(data_headers, data_list, media_files_dir, html_escape = False)
        report.end_artifact_report()

        tsvname = f'Hikvision - User Created Media'
        tsv(report_folder, data_headers, data_list, tsvname)
            
    else:
        logfunc(f'No Hikvision - User Created Media data available')

__artifacts__ = {
        "hikvision": (
                "Hikvision",
                ('*/Documents/DCLOG/YSDCLogItem.sqlite*','*/Documents/database.hik*','*/Documents/*/*/*/*.jpg','*/Documents/*/*/*/*.mov','*/Documents/*/*/*/*.mp4'),
                get_hikvision)
}
