import os
import shutil
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly

def get_googleDuo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if not file_found.endswith('DataStore'):
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
            
        cursor.execute('''
        select
        datetime(contact_reg_data_timestamp/1000000, 'unixepoch'),
        contact_name,
        contact_id,
        contact_number_label,
        datetime(contact_sync_date/1000000, 'unixepoch')
        from contact
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'Google Duo - Contacts'
            report = ArtifactHtmlReport('Google Duo - Contacts')
            report.start_artifact_report(report_folder, 'Google Duo - Contacts')
            report.add_script()
            data_headers = ('Registration Date','Name','ID','Number Label','Sync Date') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Duo - Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Duo - Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('Google Duo - Contacts data available')
            
        cursor.execute('''
        select
        datetime(call_history.call_history_timestamp, 'unixepoch'),
        call_history.call_history_local_user_id,
        call_history.call_history_other_user_id,
        contact.contact_name,
        strftime('%H:%M:%S',call_history.call_history_duration, 'unixepoch'),
        case call_history.call_history_is_outgoing_call
            when 0 then 'Incoming'
            when 1 then 'Outgoing'
        end,
        case call_history.call_history_is_video_call
            when 0 then ''
            when 1 then 'Yes'
        end
        from call_history
        left join contact on call_history.call_history_other_user_id = contact.contact_id
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'Google Duo - Call History'
            report = ArtifactHtmlReport('Google Duo - Call History')
            report.start_artifact_report(report_folder, 'Google Duo - Call History')
            report.add_script()
            data_headers = ('Timestamp','Local User ID','Remote User ID','Contact Name','Call Duration','Call Direction','Video Call?') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Duo - Call History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Duo - Call History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('Google Duo - Call History data available')
            
        cursor.execute('''
        select
        datetime(media_clip_creation_date/1000000, 'unixepoch'),
        datetime(media_clip_message_date/1000000, 'unixepoch'),
        datetime(media_clip_viewed_date/1000000, 'unixepoch'),
        media_clip_local_id,
        case media_clip_source
            when 0 then 'Received'
            when 1 then 'Sent'
        end,
        media_clip_text_representation,
        media_clip_message_id,
        media_clip_md5_checksum,
        media_clip_content_size,
        media_clip_transferred_size
        from media_clip_v2
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        
        if usageentries > 0:
            for row in all_rows:
                
                clip_creation = row[0]
                clip_message = row[1]
                clip_viewed = row[2]
                local_id = row[3]
                clip_direction = row[4]
                text_rep = row[5]
                message_id = row[6]
                content_size = row[7]
                transferred_size = row[8]
                thumb = ''
                
                clip_name = str(message_id) + '.png'
                print(clip_name)    
                #Check for Clips
                for match in files_found:
                    if clip_name in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        thumb = f'<img src="{report_folder}/{data_file_name}" width="300"></img>'
      
                data_list.append((clip_creation, clip_message, clip_viewed, local_id, clip_direction ,text_rep, message_id, content_size, transferred_size, thumb))
            
            description = 'Google Duo - Clips'
            report = ArtifactHtmlReport('Google Duo - Clips')
            report.start_artifact_report(report_folder, 'Google Duo - Clips')
            report.add_script()
            data_headers = (
                'Creation Date', 'Message Date', 'Viewed Date', 'Local User ID', 'Clip Direction','Text Representation', 'Message ID','Content Size', 'Transferred Size', 'Clip')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Clip'])
            report.end_artifact_report()
            
            tsvname = f'Google Duo - Clips'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Duo - Clips'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('Google Duo - Clips data available')    
            
        db.close()
        return

__artifacts__ = {
    "googleduo": (
        "Google Duo",
        ('*/Application Support/DataStore*','*/Application Support/ClipsCache/*.png'),
        get_googleDuo)
}