# Module Description: Parses Gmail label details and offline search content
# Author: @KevinPagano3
# Date: 2022-04-21
# Artifact version: 0.0.1
# Requirements: none

import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly

def get_Gmail(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('searchsqlitedb'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(c0/1000,'unixepoch'),
            c3 as 'Sender',
            c4 as 'Receiver',
            c5 as 'CC',
            c6 as 'BCC',
            c7 as 'Subject',
            c8 as 'Body',
            c1 as 'Thread ID',
            c2 as 'Message ID'
            from offline_search_content
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            
            if usageentries > 0:
                for row in all_rows:
                
                    sender = row[1]
                    sender_split = [sender_split.strip() for sender_split in sender.split(',')]
                    
                    if len(sender_split) < 2:
                        sender_title = sender_split[0]
                        sender_email = ''
                    else:
                        sender_title = sender_split[0]
                        sender_email = sender_split[1]

                    data_list.append((row[0], sender_title, sender_email, row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                        
                description = 'Gmail - Offline Search'
                report = ArtifactHtmlReport('Gmail - Offline Search')
                report.start_artifact_report(report_folder, 'Gmail - Offline Search')
                report.add_script()
                data_headers = (
                    'Timestamp','Sender Name','Sender Email','Receiver','CC','BCC','Subject','Body','Thread ID','Message ID')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Gmail - Offline Search'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Gmail - Offline Search'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
            else:
                logfunc('Gmail - Offline Search data available')
            
            db.close()
                    
        if file_found.endswith('sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            label_server_perm_id,
            unread_count,
            total_count,
            unseen_count
            from label_counts
            order by label_server_perm_id
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            
            if usageentries > 0:
                for row in all_rows:
                
                    data_list.append((row[0], row[1], row[2], row[3]))
                        
                description = 'Gmail - Label Details'
                report = ArtifactHtmlReport('Gmail - Label Details')
                report.start_artifact_report(report_folder, 'Gmail - Label Details')
                report.add_script()
                data_headers = (
                    'Label','Unread Count','Total Count','Unseen Count')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Gmail - Label Details'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Gmail - Label Details'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
            else:
                logfunc('Gmail - Label Details data available')
            
            db.close()

__artifacts__ = {
    "gmail": (
        "gmail",
        ('**/private/var/mobile/Containers/Data/Application/*/Library/Application Support/data/*/searchsqlitedb*','**/private/var/mobile/Containers/Data/Application/*/Library/Application Support/data/*/sqlitedb*'),
        get_Gmail)
}