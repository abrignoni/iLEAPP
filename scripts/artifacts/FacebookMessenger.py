from lib2to3.refactor import get_fixers_from_package
import sqlite3
import textwrap
from os.path import basename

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, does_table_exist, does_view_exist

def get_FacebookMessenger(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.db'):
            
            db = open_sqlite_db_readonly(file_found)
            check = does_view_exist(db, 'thread_messages')
        
            db = open_sqlite_db_readonly(file_found)
            
            if check:
                cursor = db.cursor()
                cursor.execute('''
                select
                datetime(thread_messages.timestamp_ms/1000,'unixepoch') as Timestamp,
                contacts.name as 'Sender Name',
                thread_messages.thread_key,
                thread_messages.text as 'Message',
                case thread_messages.has_attachment
                    when NULL then ''
                    when 1 then 'Yes'
                end as Attachment,
                attachments.filename as 'Attachment Name',
                attachments.filesize as 'Attachment Size',
                attachment_items.title_text
                from thread_messages
                left join contacts
                    on thread_messages.sender_id = contacts.id
                left join attachments
                    on thread_messages.message_id = attachments.message_id
                left join attachment_items
                    on thread_messages.message_id = attachment_items.message_id
                where attachment_items.title_text IS NULL or attachment_items.title_text like 'Location sharing ended'
                order by Timestamp
                ''')
        
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Facebook Messenger - Chats')
                    report.start_artifact_report(report_folder, f'Facebook Messenger - Chats - {basename(file_found)} ')
                    report.add_script()
                    data_headers = ('Timestamp','Sender Name','Sender ID','Message','Attachment','Attachment Name','Attachment Size','Title Text') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
        
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Facebook Messenger - Chats'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = f'Facebook Messenger - Chats'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f'No Facebook Messenger - Chats data available for {basename(file_found)}')
                
                cursor.execute('''
                select
                datetime(thread_messages.timestamp_ms/1000,'unixepoch') as Timestamp,
                contacts.name as 'Sender Name',
                thread_messages.thread_key,
                attachments.title_text as "Call Type",
                attachments.subtitle_text as "Duration/Subtitle"
                from thread_messages
                left join contacts
                    on thread_messages.sender_id = contacts.id
                left join attachments
                    on thread_messages.message_id = attachments.message_id
                where attachments.title_text like 'Audio Call' or attachments.title_text like 'Video Chat'
                order by Timestamp
                ''')
        
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Facebook Messenger - Calls')
                    report.start_artifact_report(report_folder, f'Facebook Messenger - Calls - {basename(file_found)}')
                    report.add_script()
                    data_headers = ('Timestamp','Sender Name','Sender ID','Call Type','Call Duration/Subtitle') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4]))
        
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Facebook Messenger - Calls'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = f'Facebook Messenger - Calls'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f'No Facebook Messenger - Calls data available for {basename(file_found)}')
            
            db = open_sqlite_db_readonly(file_found)
            check = does_table_exist(db, 'contacts')
            if check:
                cursor = db.cursor()
                cursor.execute('''
                select
                id,
                name,
                normalized_name_for_search,
                profile_picture_url,
                case is_messenger_user
                    when 0 then ''
                    when 1 then 'Yes'
                end as is_messenger_user
                from contacts
                ''')
        
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Facebook Messenger - Contacts')
                    report.start_artifact_report(report_folder, f'Facebook Messenger - Contacts - {basename(file_found)}')
                    report.add_script()
                    data_headers = ('User ID','Username','Normalized Username','Profile Pic URL','Is App User') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4]))
        
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Facebook Messenger - Contacts'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = f'Facebook Messenger - Contacts'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f'No Facebook Messenger - Contacts data available for {basename(file_found)}')
            
            db = open_sqlite_db_readonly(file_found)
            check = does_table_exist(db, 'contacts')
            if check:
                cursor = db.cursor()
                cursor.execute('''
                select
                datetime(secure_messages.timestamp_ms/1000,'unixepoch') as 'Timestamp',
                secure_messages.thread_key,
                contacts.name as 'Sender',
                secure_messages.text,
                secure_messages.secure_message_attachments_encrypted
                from secure_messages
                left join contacts
                    on secure_messages.sender_id = contacts.id
                ''')
        
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Facebook Messenger - Secret Conversation')
                    report.start_artifact_report(report_folder, f'Facebook Messenger - Secret Conversation - {basename(file_found)}')
                    report.add_script()
                    data_headers = ('Timestamp','Thread Key','Sender Name','Message (Encrypted)', 'Attachment (Encrypted)') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4]))
        
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Facebook Messenger - Secret Conversation'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = f'Facebook Messenger - Secret Conversation'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f'No Facebook Messenger - Secret Conversation data available for {basename(file_found)}')
            
            db = open_sqlite_db_readonly(file_found)
            check = does_table_exist(db, 'thread_participant_detail')
            if check:
                cursor = db.cursor()
                cursor.execute('''
                select
                datetime(threads.last_activity_timestamp_ms/1000,'unixepoch'),
                thread_participant_detail.thread_key,
                group_concat(thread_participant_detail.name, ';') 
                from thread_participant_detail
                join threads
                    on threads.thread_key = thread_participant_detail.thread_key
                group by thread_participant_detail.thread_key
                ''')
        
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Facebook Messenger - Conversation Groups')
                    report.start_artifact_report(report_folder, f'Facebook Messenger - Conversation Groups - {basename(file_found)}')
                    report.add_script()
                    data_headers = ('Timestamp (Last Activity)','Thread Key','Thread Participants') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2]))
        
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Facebook Messenger - Conversation Groups'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = f'Facebook Messenger - Conversation Groups'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f'No Facebook Messenger - Conversation Groups data available for {basename(file_found)}')
            
            

__artifacts__ = {
    "facebookmessenger": (
        "Facebook Messenger",
        ('**/lightspeed-*.db*'),
        get_FacebookMessenger)
}