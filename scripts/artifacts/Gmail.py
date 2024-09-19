__artifacts_v2__ = {
    "gmail_offline_search": {
        "name": "Gmail - Offline Search",
        "description": "Parses Gmail offline search content",
        "author": "@KevinPagano3",
        "version": "0.0.2",
        "date": "2024-03-20",
        "requirements": "none",
        "category": "Gmail",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/searchsqlitedb*',),
        "output_types": "all"
    },
    "gmail_label_details": {
        "name": "Gmail - Label Details",
        "description": "Parses Gmail label details",
        "author": "@KevinPagano3",
        "version": "0.0.2",
        "date": "2024-03-20",
        "requirements": "none",
        "category": "Gmail",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/sqlitedb*',),
        "output_types": "all"
    }
}

# from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor

@artifact_processor(__artifacts_v2__["gmail_offline_search"])
def get_Gmail_offline_search(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''
    
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        
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
            
            db.close()
    
    data_headers = (
        ('Timestamp', 'datetime'), 'Sender Name', 'Sender Email', 'Receiver', 'CC', 'BCC', 'Subject', 'Body', 'Thread ID', 'Message ID'
    )
    
    return data_headers, data_list, source_path

@artifact_processor(__artifacts_v2__["gmail_label_details"])
def get_Gmail_label_details(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''
    
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        
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
            
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))
            
            db.close()
    
    data_headers = ('Label', 'Unread Count', 'Total Count', 'Unseen Count')
    
    return data_headers, data_list, source_path
